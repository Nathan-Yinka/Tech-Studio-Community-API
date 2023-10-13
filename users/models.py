from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Group, Permission
import uuid
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)
    
    def get_queryset(self):
        return super().get_queryset().filter()
    
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    community = models.ForeignKey("Community", on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='user_profile_pic',null=True,blank=True)
    following = models.ManyToManyField('self',through='Contact',related_name='followers',symmetrical=False)
       
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='custom_user_groups',
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_user_permissions',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        unique_together = ('email', 'is_active')
        
        indexes = [
            models.Index(fields=['id']), 
        ]
        ordering = ["id"]
    
class EmailConfirmationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class PasswordResetConfirmationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Community(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Contact(models.Model):
    user_from = models.ForeignKey('User',related_name='rel_from_set',on_delete=models.CASCADE)   
    user_to = models.ForeignKey('User',related_name='rel_to_set',on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
        models.Index(fields=['-created']),
        ]
        ordering = ['-created']
        
    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'
    

