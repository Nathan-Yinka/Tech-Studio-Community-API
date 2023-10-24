from django.urls import path
from . import views

app_name = "post"

urlpatterns = [
    path("",views.PostListCreateView.as_view(), name = "post-list-create"),
    path("<int:pk>/",views.PostRetrieveDestroyView.as_view(),name="post-detail"),
    path("comment/",views.CommentCreateView.as_view(), name = "comment-create"),
]
