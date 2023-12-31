from django.urls import path
from django.contrib.auth import get_user_model
from . import views

app_name = "auth"

urlpatterns = [
    path("register/",views.UserRegistrationView.as_view(), name = "register"),
    path('confirm-email/', views.EmailConfirmationView.as_view(), name='confirm-email'),
    path("resend-confimation/",views.ResendConfirmationEmailView.as_view(),name="resend-confimation"),
    path("login/",views.UserLoginView.as_view(), name = "user-login"),
    path("user/",views.AuthenticatedUserView.as_view(), name = "authenticated-user"),
    
    path("reset-password/",views.PasswordResetRequestView.as_view(),name='reset-password'),
    path("confirm-password-reset/",views.PasswordResetConfirmView.as_view(),name="confirm-password-reset"),
]
