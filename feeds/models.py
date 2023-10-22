from django.db import models
from users.models import Community
from django.contrib.auth import get_user_model
import os

User = get_user_model()

def validate_file_extension(value):
   
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # Get the file extension
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mkv', '.mov']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Please upload an image or video.')
    
def user_thumbnail_directory_path(instance, filename):
    email = instance.user.email
    email = email.replace('@', '_').replace('.', '_')

    ext = os.path.splitext(filename)[1]
    
    return f'thumbnails/{email}/{filename}'
    
def user_media_directory_path(instance, filename):
    email = instance.user.email
    email = email.replace('@', '_').replace('.', '_')

    folder_name = "project" if instance.project else "post"

    ext = os.path.splitext(filename)[1]

    return f'{folder_name}/{email}/{filename}'

class Feed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="user_feeds") 
    title = models.CharField(max_length=100)
    tag = models.ForeignKey(Community, on_delete=models.CASCADE)
    tools = models.CharField(max_length=250, null=True, blank=True)
    url = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField(null=True,blank=True)
    media_file = models.FileField(upload_to=user_media_directory_path, validators=[validate_file_extension],null=True,blank=True)
    thumbnail = models.ImageField(upload_to=user_thumbnail_directory_path,null=True,blank=True)
    likes = models.ManyToManyField(User, related_name='liked_projects', blank=True)
    total_likes = models.PositiveIntegerField(default=0,null=True,blank=True)
    project = models.BooleanField(default=False,null=True,blank=True)
    post = models.BooleanField(default=False,null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)
    views_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    
    def __str__(self):
        type_str = ""
        if self.post:
            type_str = "post"
        elif self.project:
            type_str = "project"

        return f"{self.title} ({type_str})"
    
    class Meta:
        ordering = ['-created']
    
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="feed_comments")
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.feed}'

    class Meta:
        ordering = ['-created']
    