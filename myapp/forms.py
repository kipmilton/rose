from django import forms
from django.contrib.auth.models import User

from .models import (
    Assignment,
    BlogPost,
    SiteSettings,
    Subject,
    SubjectQuestion,
    Submission,
    SystemUpdate,
)


INPUT_CLASS = 'form-control'
TEXTAREA_CLASS = 'form-control'
SELECT_CLASS = 'form-select'


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'teacher_name', 'description', 'image', 'notes_pdf']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Subject name'}),
            'teacher_name': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 2, 'placeholder': 'Enter teacher name'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4, 'placeholder': 'What should learners know about this subject?'}),
            'image': forms.ClearableFileInput(attrs={'class': INPUT_CLASS, 'accept': 'image/*'}),
            'notes_pdf': forms.ClearableFileInput(attrs={'class': INPUT_CLASS, 'accept': 'application/pdf'}),
        }


class AssignmentForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': INPUT_CLASS, 'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Assignment
        fields = ['title', 'description', 'subject', 'due_date', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Assignment title'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4, 'placeholder': 'Instructions for students'}),
            'subject': forms.Select(attrs={'class': SELECT_CLASS}),
            'file': forms.ClearableFileInput(attrs={'class': INPUT_CLASS}),
        }


class GradeForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['grade']
        widgets = {
            'grade': forms.Select(attrs={'class': SELECT_CLASS}),
        }


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': INPUT_CLASS}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': INPUT_CLASS}), label='Confirm Password')

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password']
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT_CLASS}),
        }
        labels = {
            'username': 'Admission No./Username',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': INPUT_CLASS}),
        }


class SubjectQuestionForm(forms.ModelForm):
    class Meta:
        model = SubjectQuestion
        fields = ['question_text']
        widgets = {
            'question_text': forms.Textarea(
                attrs={
                    'class': TEXTAREA_CLASS,
                    'rows': 4,
                    'placeholder': 'Ask your teacher about this subject, topic, or notes...',
                }
            ),
        }


class SubjectQuestionResponseForm(forms.ModelForm):
    class Meta:
        model = SubjectQuestion
        fields = ['teacher_response']
        widgets = {
            'teacher_response': forms.Textarea(
                attrs={
                    'class': TEXTAREA_CLASS,
                    'rows': 3,
                    'placeholder': 'Respond to the learner here...',
                }
            ),
        }


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'category', 'excerpt', 'image', 'published_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'category': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'excerpt': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4}),
            'image': forms.ClearableFileInput(attrs={'class': INPUT_CLASS, 'accept': 'image/*'}),
            'published_at': forms.DateTimeInput(attrs={'class': INPUT_CLASS, 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }


class SystemUpdateForm(forms.ModelForm):
    class Meta:
        model = SystemUpdate
        fields = ['title', 'content', 'published_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'content': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4}),
            'published_at': forms.DateTimeInput(attrs={'class': INPUT_CLASS, 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ['site_name', 'logo']
        widgets = {
            'site_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'logo': forms.ClearableFileInput(attrs={'class': INPUT_CLASS, 'accept': 'image/*'}),
        }
