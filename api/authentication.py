from rest_framework.authentication import TokenAuthentication as BaseTokenAuth,SessionAuthentication
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from rest_framework import exceptions
User = get_user_model()

class TokenAuthentication(BaseTokenAuth):
    keyword = "Bearer"
    
class StaffUserTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        if not token.user.is_staff:
            raise exceptions.AuthenticationFailed(_('User is not a superuser.'))

        return (token.user, token)
    
class StaffUserSessionAuthentication(SessionAuthentication):
    
    def authenticate(self, request):
        auth_result = super().authenticate(request)
        
        if auth_result is None:
            return None 
        user, _ = auth_result
        if user and user.is_staff:
            return user, None
        return None
    
    
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
