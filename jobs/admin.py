from django.contrib import admin
from .models import JobPost,Skill,Tool,JobPoster

# Register your models here.
admin.site.register(JobPost)
admin.site.register(JobPoster)
admin.site.register(Skill)
admin.site.register(Tool)
