from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField

from django.db.models import CharField, ImageField, DateTimeField,BooleanField, TextField, EmailField

class BlogPost(models.Model):
    """
    Model to store blog posts for the AI/ML blog.
    """
    title = CharField(max_length=50)
    slug = CharField(max_length=255, unique=True, blank=True)
    content = TextField()
    image = ImageField(upload_to='blog_images/')
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    is_published = BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    class meta: 
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['-created_at']


class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError('The email field must be set')
        if not phone_number:
            raise ValueError('the phone number field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, phone_number, password, **extra_fields)
    
    

class CustomUser(AbstractUser):
   
    phone_number = PhoneNumberField(unique=True, null=False, blank=False)
    email = EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email

    
    
        
        
        
    
        
        
        
        
        
        
        
        
        
    
