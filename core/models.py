from django.db import models
from django.utils import timezone

# Create your models here.
class AllowedEmail(models.Model):
    email = models.EmailField(unique=True)
    created = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.email