from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Community,EmailConfirmationToken
from PIL import Image
from resizeimage import resizeimage

from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

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
            raise ValidationError('An account with this email address already exists and is active.')
        return value
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = self.Meta.model(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def validate_image(self, value):
        # Custom validation for the uploaded image goes here if needed.
        # You can also perform resizing here before saving.

        if value:
            # Resize the image to 200x200 pixels
            img = Image.open(value)
            img = resizeimage.resize_thumbnail(img, [500, 500])

            # Save the resized image back to the same field
            value.seek(0)  # Make sure the file is at the beginning
            img.save(value, img.format)
            value.seek(0)  # Reset the file pointer

        return value
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    
class CommumitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = "__all__"
        
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, required=True)