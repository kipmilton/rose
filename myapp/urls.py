from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views


app_name = 'myapp'

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('accounts/login/', views.login_page, name='login_page'),
    path('accounts/register/', views.register, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('subjects/', views.subjects, name='subjects_page'),
    path('subjects/<int:id>/', views.subject_detail, name='subject_detail'),
    path('about/', views.about, name='about'),
    path('parent-portal/', views.parent_portal, name='parent_portal'),
    path('teachers-dashboard/', views.teachers_dashboard, name='teachers_dashboard'),
    path('add-subject/', views.add_subject, name='add_subject'),
    path('subjects/<int:subject_id>/update/', views.update_subject_assets, name='update_subject_assets'),
    path('submissions/', views.view_submissions, name='view_submissions'),
    path('grade/<int:submission_id>/', views.grade_submission, name='grade_submission'),
    path('upload-assignment/', views.upload_assignment, name='upload_assignment'),
    path('assignments/<int:id>/', views.assignment_detail, name='assignment_detail'),
    path('assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('delete-subject/<int:subject_id>/', views.delete_subject, name='delete_subject'),
    path('delete-assignment/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),
    path('teachers-delete/', views.teachers_delete, name='teachers_delete'),
    path('blog-posts/create/', views.create_blog_post, name='create_blog_post'),
    path('blog-posts/<int:post_id>/edit/', views.edit_blog_post, name='edit_blog_post'),
    path('system-updates/create/', views.create_system_update, name='create_system_update'),
    path('system-updates/<int:update_id>/edit/', views.edit_system_update, name='edit_system_update'),
    path('branding/update/', views.update_branding, name='update_branding'),
    path('questions/<int:question_id>/respond/', views.respond_question, name='respond_question'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
