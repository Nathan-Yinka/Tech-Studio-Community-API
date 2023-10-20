from django.urls import path
from . import views

app_name="core"

urlpatterns = [
    path("",views.AllowEmailView.as_view(), name="user"),
    path("<int:pk>",views.AllowEmailDeleteView.as_view(), name="user-delete"),
    path("login/",views.SuperUserLoginView.as_view(),name="login-superuser"),
    path("jobs/",views.JobPostViewSet.as_view(),name="jobs"),
    path("csv-upload/",views.AllowedEmailCSVUploadView.as_view(),name="csv-upload"),
]
