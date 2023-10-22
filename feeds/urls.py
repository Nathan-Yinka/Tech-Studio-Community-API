from django.urls import path
from . import views

app_name = "project"

urlpatterns = [
    path("",views.ProjectListCreateView.as_view(),name="list-create"),
    path("<int:pk>/",views.ProjectRetrieveUpdateDestroyView.as_view(),name="project-detail"),
    path("like-unlike/",views.LikeUnlikeFeedView.as_view(), name="like-unlike"),
    path("user-projects/", views.UserProjectsListView.as_view(), name="user-projects-list"),
]
