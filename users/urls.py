from django.urls import path
from django.contrib.auth import get_user_model
from . import views

app_name = "user"
urlpatterns = [
    path("register/",views.UserRegistrationView.as_view(), name = "register"),
    path('confirm-email/<str:uid>/<str:token>/', views.EmailConfirmationView.as_view(), name='confirm-email'),
    path("resend-confimation/",views.ResendConfirmationEmailView.as_view(),name="resend-confimation"),
    path("login/",views.UserLoginView.as_view(), name = "user-list"),
    
    path("users/",views.UserListView.as_view(), name = "user-list"),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    
    path("community/",views.CommunityListView.as_view(), name = "community-list"),
]
