from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Action(models.Model):
    user = models.ForeignKey(User,related_name='actions',on_delete=models.CASCADE)
    verb = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    recipient = models.ForeignKey(User, related_name='received_actions', on_delete=models.CASCADE)
    target_ct = models.ForeignKey(ContentType,blank=True,null=True,related_name='target_obj',on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField(null=True,blank=True)
    target = GenericForeignKey('target_ct', 'target_id')
    read = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['target_ct', 'target_id']),
        ]
        ordering = ['-created']