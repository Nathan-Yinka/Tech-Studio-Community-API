from rest_framework import serializers
from .models import Feed,Comment
from django.contrib.auth import get_user_model
from notifications.serializers import UserSerializer
from django.core.cache import cache
from django.contrib.humanize.templatetags import humanize
from users.serializers import CommumitySerializer

User = get_user_model()


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        exclude = ["user","likes","total_likes","project","post","views_count"]
        
class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ["description","media_file"]
        
class ProjectSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    liked_by_user = serializers.SerializerMethodField(read_only=True)
    file_type = serializers.SerializerMethodField(read_only=True)
    views = serializers.SerializerMethodField(read_only=True)
    created = serializers.SerializerMethodField(read_only=True)
    month = serializers.SerializerMethodField(read_only=True)
    tag = CommumitySerializer(read_only=True)
    class Meta:
        model = Feed
        exclude = ["project","post","views_count"]
        
    def get_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.likes.all()
        return False
    
    def get_file_type(self, obj):
        file_extension = obj.media_file.name.split('.')[-1].lower()

        if file_extension in ('jpg', 'jpeg', 'png', 'gif'):
            return 'image'
        elif file_extension in ('mp4', 'avi', 'mkv', 'mov'):
            return 'video'
        else:
            return 'unknown'
    
    def get_views(self, obj):
        cache_key = f'feed_views_{obj.id}'
        view_count = cache.get(cache_key)
        if view_count is not None:
            return view_count
        else:
            return obj.views_count
    
    def get_created(self, obj):
        return humanize.naturaltime(obj.created)
    
    def get_month(self, obj):
        created_time = obj.created
        created_date = created_time.strftime("%B %d")
        return created_date
    
class PostSerializer(ProjectSerializer):
    comment_number = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)
    
    def get_comment_number(self, obj):
        return obj.feed_comments.all().count()
    
    def get_comments(self, obj):
        comments = obj.feed_comments.all()
        comment_serializer = CommentSerializer(comments, many=True)
        return comment_serializer.data
    
        
class FeedLikeUnlikeSerializer(serializers.Serializer):
    feed_id = serializers.IntegerField()
    
class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["text","feed"]
        
class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    created = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Comment
        exclude =["feed"]
        
    def get_created(self, obj):
        return humanize.naturaltime(obj.created)