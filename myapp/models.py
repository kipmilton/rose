from django.conf import settings
from django.db import models
from django.utils import timezone


User = settings.AUTH_USER_MODEL


class Subject(models.Model):
    name = models.CharField(max_length=100, default='Chemistry')
    description = models.TextField(default='CBC')
    teacher_name = models.CharField(max_length=150, blank=True, default='')
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='subjects',
    )
    image = models.ImageField(upload_to='subjects/', blank=True, null=True)
    notes_pdf = models.FileField(upload_to='subject_notes/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    @property
    def teacher_display_name(self):
        if self.teacher_name.strip():
            return self.teacher_name.strip()
        if not self.teacher:
            return 'Teacher not assigned'
        full_name = self.teacher.get_full_name().strip()
        return full_name or self.teacher.username


class Assignment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

    title = models.CharField(max_length=255, default='Our Subjects')
    description = models.TextField(default='CBC')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    due_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    file = models.FileField(upload_to='assignments/', blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def teacher_display_name(self):
        full_name = self.teacher.get_full_name().strip()
        return full_name or self.teacher.username


class SubjectQuestion(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subject_questions')
    question_text = models.TextField()
    teacher_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student} - {self.subject}'


class Submission(models.Model):
    STATUS_CHOICES = [
        ('Attempted', 'Attempted'),
        ('Completed', 'Completed'),
    ]
    GRADE_CHOICES = [
        ('Normal Expectation (90-100%)', 'Normal Expectation (90-100%)'),
        ('Exceptional (72-89%)', 'Exceptional (72-89%)'),
        ('Meeting Expectation (58-74%)', 'Meeting Expectation (58-74%)'),
        ('Good (41-57%)', 'Good (41-57%)'),
        ('Approaching Expectation (24-40%)', 'Approaching Expectation (24-40%)'),
        ('Below Expectation (0-23%)', 'Below Expectation (0-23%)'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    image = models.FileField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Attempted')
    grade = models.CharField(max_length=64, choices=GRADE_CHOICES, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'assignment')
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.student} - {self.assignment.title}'


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, default='Education News')
    excerpt = models.TextField()
    image = models.ImageField(upload_to='blog_posts/', blank=True, null=True)
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class SystemUpdate(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=120, default='Master CBC')
    logo = models.ImageField(upload_to='branding/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.site_name
