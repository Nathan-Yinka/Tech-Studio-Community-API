from django.urls import path, include
from rest_framework import routers
from .views import JobPostViewSet
from . import views

urlpatterns = [
    # Your other URL patterns
    path("",views.JobPosterView.as_view(), name = "posters"),    # the path for all the client to post jobs
    path('posts',views.JobPostViewSet.as_view()),                #all posted jobs
    path("skills/",views.SkillCreateView.as_view(),name="create-skill"),    #all the skills creation
    path("tools/",views.ToolCreateView.as_view(),name="create-skill"),    #all the tools creation
    path('dropdown/', views.DropDownItem.as_view(), name='dropdown-item'),   # the dropdown information 
]
