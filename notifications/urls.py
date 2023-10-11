from django.urls import path
from . import views

app_name = "notification"

urlpatterns = [
    path("",views.NotificationAPIView.as_view(),name="notifications"),
    path('<int:id>/', views.NotificationUpdateAPIView.as_view(), name='update-read'),
]
