from rest_framework.authentication import TokenAuthentication as BaseTokenAuth
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
User = get_user_model()

class TokenAuthentication(BaseTokenAuth):
    keyword = "Bearer"
    
    
class CustomAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
