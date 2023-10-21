from django.db import models
from users.models import Community
from django.contrib.auth import get_user_model

User = get_user_model()

def validate_file_extension(value):
    import os
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

    ext = os.path.splitext(filename)[1]

    return f'project/{email}/{filename}'

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    title = models.CharField(max_length=100)
    tag = models.ForeignKey(Community, on_delete=models.CASCADE)
    tools = models.CharField(max_length=250, null=True, blank=True)
    url = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField()
    media_file = models.FileField(upload_to=user_media_directory_path, validators=[validate_file_extension])
    thumbnail = models.ImageField(upload_to=user_thumbnail_directory_path)
    
    def __str__(self):
        return self.title
