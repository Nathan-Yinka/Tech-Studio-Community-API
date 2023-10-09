from django.urls import path
from django.contrib.auth import get_user_model
from . import views
from . import allowed_users

app_name = "user"
urlpatterns = [
    path("register/",views.UserRegistrationView.as_view(), name = "register"),
    path('confirm-email/', views.EmailConfirmationView.as_view(), name='confirm-email'),
    path("resend-confimation/",views.ResendConfirmationEmailView.as_view(),name="resend-confimation"),
    path("login/",views.UserLoginView.as_view(), name = "user-list"),
    
    path("reset-password/",views.PasswordResetRequestView.as_view(),name='reset-password'),
    path("confirm-password-reset/",views.PasswordResetConfirmView.as_view(),name="confirm-password-reset"),
    
    path("users/",views.UserListView.as_view(), name = "user-list"),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    
    path("community/",views.CommunityListView.as_view(), name = "community-list"),
    
    path('user-follow/', views.UserFollow.as_view(), name='user-follow'),
    path('user-unfollow/', views.UserUnfollow.as_view(), name='user-unfollow'),
    
    # user upload endpoint
    path('allowed-users-upload/', allowed_users.superuser_upload_view, name="allowed-users-upload"),
]
