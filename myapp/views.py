from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    AssignmentForm,
    BlogPostForm,
    GradeForm,
    RegisterForm,
    SiteSettingsForm,
    SubjectForm,
    SubjectQuestionForm,
    SubjectQuestionResponseForm,
    SubmissionForm,
    SystemUpdateForm,
)
from .models import (
    Assignment,
    BlogPost,
    SiteSettings,
    Subject,
    SubjectQuestion,
    Submission,
    SystemUpdate,
)


GRADING_GUIDE = Submission.GRADE_CHOICES


def is_teacher(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def get_site_settings():
    settings_obj, _ = SiteSettings.objects.get_or_create(pk=1)
    return settings_obj


def build_dashboard_context(request):
    return {
        'subject_form': SubjectForm(),
        'assignment_form': AssignmentForm(),
        'blog_post_form': BlogPostForm(),
        'system_update_form': SystemUpdateForm(),
        'site_settings_form': SiteSettingsForm(instance=get_site_settings()),
        'subjects': Subject.objects.select_related('teacher').all().order_by('name'),
        'assignments': Assignment.objects.select_related('subject', 'teacher').all().order_by('-created_at'),
        'submissions': Submission.objects.select_related('student', 'assignment__subject').all(),
        'questions': SubjectQuestion.objects.select_related('student', 'subject').all(),
        'blog_posts': BlogPost.objects.all(),
        'system_updates': SystemUpdate.objects.all(),
        'site_settings': get_site_settings(),
    }



def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('myapp:home_page')
        messages.error(request, 'Invalid credentials')
    return render(request, 'accounts/login.html', {'site_settings': get_site_settings()})



def logout_user(request):
    logout(request)
    return redirect('myapp:login_page')



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully.')
            return redirect('myapp:login_page')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form, 'site_settings': get_site_settings()})


@login_required
@user_passes_test(is_teacher)
def teachers_dashboard(request):
    context = build_dashboard_context(request)
    return render(request, 'teachers.html', context)


@login_required
def subjects(request):
    context = {
        'subjects': Subject.objects.select_related('teacher').all().order_by('name'),
        'site_settings': get_site_settings(),
    }
    return render(request, 'subjects.html', context)


@login_required
def subjects_assignments_view(request):
    return redirect('myapp:subjects_page')


@login_required
@user_passes_test(is_teacher)
def view_submissions(request):
    submissions = Submission.objects.select_related('student', 'assignment__subject').all()
    return render(
        request,
        'view_submissions.html',
        {'submissions': submissions, 'site_settings': get_site_settings()},
    )


@login_required
@user_passes_test(is_teacher)
def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission.objects.select_related('student', 'assignment__subject'), id=submission_id)
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=submission)
        if form.is_valid():
            graded_submission = form.save(commit=False)
            graded_submission.status = 'Completed'
            graded_submission.save()
            messages.success(request, 'Grade updated!')
            return redirect('myapp:teachers_dashboard')
    else:
        form = GradeForm(instance=submission)
    return render(
        request,
        'grade_submission.html',
        {
            'form': form,
            'submission': submission,
            'grading_guide': GRADING_GUIDE,
            'site_settings': get_site_settings(),
        },
    )



def home_page(request):
    context = {
        'subjects': Subject.objects.select_related('teacher').all().order_by('name'),
        'assignments': Assignment.objects.select_related('subject', 'teacher').all().order_by('-created_at'),
        'latest_done_assignments': Submission.objects.filter(status='Completed').select_related(
            'assignment__subject', 'student'
        )[:5],
        'blog_posts': BlogPost.objects.all()[:6],
        'system_updates': SystemUpdate.objects.all()[:4],
        'site_settings': get_site_settings(),
    }
    return render(request, 'index.html', context)



def about(request):
    return render(request, 'about.html', {'site_settings': get_site_settings()})



def subject_detail(request, id):
    subject = get_object_or_404(Subject.objects.select_related('teacher'), id=id)
    question_history = SubjectQuestion.objects.none()

    if request.user.is_authenticated:
        question_history = SubjectQuestion.objects.filter(
            subject=subject,
            student=request.user,
        ).order_by('-created_at')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to ask a question.')
            return redirect('myapp:login_page')
        question_form = SubjectQuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.subject = subject
            question.student = request.user
            question.save()
            messages.success(request, 'Your question has been sent to the teacher.')
            return redirect('myapp:subject_detail', id=subject.pk)
    else:
        question_form = SubjectQuestionForm()

    return render(
        request,
        'subject_detail.html',
        {
            'subject': subject,
            'question_form': question_form,
            'question_history': question_history,
            'site_settings': get_site_settings(),
        },
    )



def assignment_detail(request, id):
    assignment = get_object_or_404(Assignment.objects.select_related('subject', 'teacher'), id=id)
    existing_submission = None
    if request.user.is_authenticated:
        existing_submission = Submission.objects.filter(student=request.user, assignment=assignment).first()
    return render(
        request,
        'assignment_detail.html',
        {
            'assignment': assignment,
            'existing_submission': existing_submission,
            'site_settings': get_site_settings(),
        },
    )


@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment.objects.select_related('subject', 'teacher'), id=assignment_id)
    submission, _ = Submission.objects.get_or_create(student=request.user, assignment=assignment)

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            saved_submission = form.save(commit=False)
            saved_submission.status = 'Attempted'
            saved_submission.submitted_at = timezone.now()
            saved_submission.save()
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('myapp:subjects_page')
    else:
        form = SubmissionForm(instance=submission)

    return render(
        request,
        'submit_assignment.html',
        {
            'assignment': assignment,
            'submission': submission,
            'form': form,
            'site_settings': get_site_settings(),
        },
    )


@login_required
@user_passes_test(is_teacher)
def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject created successfully.')
        else:
            messages.error(request, 'Please review the subject form and try again.')
    return redirect('myapp:teachers_dashboard')


@login_required
@user_passes_test(is_teacher)
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, 'Subject deleted.')
    return redirect('myapp:teachers_dashboard')


@login_required
@user_passes_test(is_teacher)
def upload_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = request.user
            assignment.save()
            messages.success(request, 'Assignment uploaded successfully.')
        else:
            messages.error(request, 'Please review the assignment form and try again.')
    return redirect('myapp:teachers_dashboard')


@login_required
@user_passes_test(is_teacher)
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    assignment.delete()
    messages.success(request, 'Assignment deleted.')
    return redirect('myapp:teachers_dashboard')


@login_required
@user_passes_test(is_teacher)
def teachers_delete(request):
    subjects = Subject.objects.select_related('teacher').all().order_by('name')
    assignments = Assignment.objects.select_related('subject', 'teacher').all().order_by('-created_at')
    return render(
        request,
        'teachers_delete.html',
        {'subjects': subjects, 'assignments': assignments, 'site_settings': get_site_settings()},
    )


@login_required
@user_passes_test(is_teacher)
def create_blog_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post saved.')
        else:
            messages.error(request, 'Please review the blog post fields.')
    return redirect('myapp:teachers_dashboard')


@login_required
@user_passes_test(is_teacher)
def edit_blog_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated.')
            return redirect('myapp:teachers_dashboard')
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'edit_blog_post.html', {'form': form, 'post': post, 'site_settings': get_site_settings()})


@login_required
@user_passes_test(is_teacher)
def create_system_update(request):
    if request.method == 'POST':
        form = SystemUpdateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'System update published.')
        else:
            messages.error(request, 'Please review the system update fields.')
    return redirect('myapp:teachers_dashboard')


@login_required
@user_passes_test(is_teacher)
def edit_system_update(request, update_id):
    update = get_object_or_404(SystemUpdate, id=update_id)
    if request.method == 'POST':
        form = SystemUpdateForm(request.POST, instance=update)
        if form.is_valid():
            form.save()
            messages.success(request, 'System update updated.')
            return redirect('myapp:teachers_dashboard')
    else:
        form = SystemUpdateForm(instance=update)
    return render(request, 'edit_system_update.html', {'form': form, 'update_item': update, 'site_settings': get_site_settings()})


@login_required
@user_passes_test(is_teacher)
def update_branding(request):
    settings_obj = get_site_settings()
    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branding updated successfully.')
        else:
            messages.error(request, 'Please review the branding fields.')
    return redirect('myapp:teachers_dashboard')


@login_required
@user_passes_test(is_teacher)
def respond_question(request, question_id):
    question = get_object_or_404(SubjectQuestion, id=question_id)
    if request.method == 'POST':
        form = SubjectQuestionResponseForm(request.POST, instance=question)
        if form.is_valid():
            response = form.save(commit=False)
            if response.teacher_response:
                response.responded_at = timezone.now()
            response.save()
            messages.success(request, 'Response saved.')
        else:
            messages.error(request, 'Please review the response and try again.')
    return redirect('myapp:teachers_dashboard')


@login_required
@user_passes_test(is_teacher)
def update_subject_assets(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, request.FILES, instance=subject)
        if form.is_valid():
            updated_subject = form.save(commit=False)
            if not updated_subject.teacher:
                updated_subject.teacher = request.user
            updated_subject.save()
            messages.success(request, 'Subject details updated.')
        else:
            messages.error(request, 'Please review the subject details form.')
    return redirect('myapp:teachers_dashboard')



def parent_portal(request):
    username = request.GET.get('username', '').strip()
    student_record = None
    submissions = Submission.objects.none()
    progress_summary = []
    overall_progress = None
    progress_width = '0%'

    if username:
        student_record = User.objects.filter(username=username).first()
        if student_record:
            submissions = Submission.objects.filter(student=student_record).select_related('assignment__subject')
            subjects = Subject.objects.filter(assignments__submissions__student=student_record).distinct().order_by('name')
            total_assignments = Assignment.objects.filter(subject__in=subjects).count()
            completed_count = submissions.filter(status='Completed').count()
            if total_assignments:
                overall_progress = round((completed_count / total_assignments) * 100)
            else:
                overall_progress = 0

            progress_width = f'{overall_progress}%'

            for subject in subjects:
                subject_assignments = Assignment.objects.filter(subject=subject).count()
                subject_submissions = submissions.filter(assignment__subject=subject)
                subject_completed = subject_submissions.filter(status='Completed').count()
                progress = round((subject_completed / subject_assignments) * 100) if subject_assignments else 0
                
                # Get the latest submission to safely access grade
                latest_submission = subject_submissions.first()
                latest_grade = latest_submission.grade if latest_submission else None
                
                progress_summary.append(
                    {
                        'subject': subject,
                        'scores': [item.grade for item in subject_submissions if item.grade],
                        'latest_grade': latest_grade,
                        'submitted': subject_submissions.count(),
                        'progress': progress,
                        'progress_width': f'{progress}%',
                    }
                )
        else:
            messages.error(request, 'No student found with that admission number.')

    return render(
        request,
        'parent_portal.html',
        {
            'site_settings': get_site_settings(),
            'student_record': student_record,
            'submissions': submissions,
            'progress_summary': progress_summary,
            'overall_progress': overall_progress,
            'progress_width': progress_width,
            'search_username': username,
        },
    )
