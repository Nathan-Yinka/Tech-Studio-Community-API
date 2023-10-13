from rest_framework import serializers
from .models import AllowedEmail
from django.contrib.auth import get_user_model

User = get_user_model()

class CSVFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class AllowedEmailSerializer(serializers.ModelSerializer):
    is_registered_user = serializers.SerializerMethodField()
    class Meta:
        model = AllowedEmail
        fields = "__all__"
        
    def validate_email(self, value):
        # Add your custom validation logic here
        if not value:
            raise serializers.ValidationError("Email field is required.")
        
        if AllowedEmail.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")

        return value
    
    def get_is_registered_user(self, obj):
        try:
            user = User.objects.get(email=obj.email)
            return True
        except User.DoesNotExist:
            return False
    
    