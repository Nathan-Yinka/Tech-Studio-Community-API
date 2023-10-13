from django.urls import path
from . import views

app_name="core"
urlpatterns = [
    path("login/",views.SuperUserLoginView.as_view(),name="login-superuser"),
    path("jobs/",views.JobPostViewSet.as_view(),name="jobs"),
    path("users-upload/",views.AllowedEmailCSVUploadView.as_view(),name="user-upload"),
]
