from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Community,EmailConfirmationToken,Contact
from PIL import Image
from resizeimage import resizeimage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'first_name', 'last_name','fullname','community', 'image')

class FollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'first_name', 'last_name',"fullname", 'community', 'image')

class CustomUserSerializer(serializers.ModelSerializer):
    community_name = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    followers_count = serializers.SerializerMethodField(read_only=True)
    following_count = serializers.SerializerMethodField(read_only=True) 
    followers = FollowerSerializer(many=True, read_only=True) 
    following = FollowingSerializer(many=True, read_only=True)  
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['is_following'] = serializers.SerializerMethodField(read_only=True)
            
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'community','full_name', 'image','followers_count', 'following_count','followers', 'following',"community_name")
        extra_kwargs = {'password': {'write_only': True}}
        error_messages = {
            'email': {
                'unique': 'A user with this email already exists.cccvvvfdhd'
            }
        }
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
        
    def validate_email(self, value):
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
    
    def get_community_name(self, obj):
        return obj.community.name if obj.community else None
    
    def validate_image(self, value):
        if value:
            img = Image.open(value)
            img = resizeimage.resize_thumbnail(img, [500, 500])
            value.seek(0) 
            img.save(value, img.format)
            value.seek(0) 
        return value
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.following.filter(id=obj.id).exists()
        return False
    
    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()
    
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
    
class EmailConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    
class ResendConfirmationEmailSerializer(serializers.Serializer):
    uid =serializers.CharField()
    
class FollowUnfollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields =["user_to"]