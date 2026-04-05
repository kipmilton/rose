from django.contrib import admin

from .models import Assignment, BlogPost, SiteSettings, Subject, SubjectQuestion, Submission, SystemUpdate


admin.site.register(Subject)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(SubjectQuestion)
admin.site.register(BlogPost)
admin.site.register(SystemUpdate)
admin.site.register(SiteSettings)
