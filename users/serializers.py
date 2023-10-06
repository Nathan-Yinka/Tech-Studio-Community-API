from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Community,EmailConfirmationToken

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'community', 'image')
        extra_kwargs = {'password': {'write_only': True}}
        error_messages = {
            'email': {
                'unique': 'A user with this email already exists.cccvvvfdhd'
            }
        }
        
    def validate_email(self, value):
        # Your custom email validation logic here
        # Check if an active user with the same email exists
        if get_user_model().objects.filter(email=value, is_active=True).exists():
            raise ValidationError('An account with this email address already exists and is active. kfjdjfjjffjk')
        return value
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = self.Meta.model(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    
class CommumitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = "__all__"