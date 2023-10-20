from django.urls import path
from django.contrib.auth import get_user_model
from . import views


app_name = "user"

urlpatterns = [
    path("",views.UserListView.as_view(), name = "user-list"),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    
    path("community/",views.CommunityListView.as_view(), name = "community-list"),
    path("community/<int:pk>/",views.CommunityRetrieveView.as_view(), name = "community-retrieve"),
    
    path('follow/', views.UserFollow.as_view(), name='user-follow'),
    path('unfollow/', views.UserUnfollow.as_view(), name='user-unfollow'),
    
    # user upload endpoint
#     path('allowed-users-upload/', allowed_users.superuser_upload_view, name="allowed-users-upload"),
]
