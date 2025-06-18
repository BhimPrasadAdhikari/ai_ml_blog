from django.db import models
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .constants import PostStatus, CommentStatus
from django.contrib.auth.models import BaseUserManager
from django.utils.text import slugify


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, phone_number, password=None, username=None, **extra_fields):
        if not email:
            raise ValueError('The email field must be set')
        if not phone_number:
            raise ValueError('the phone number field must be set')
        email = self.normalize_email(email)

        if not username:
            username = email.split('@')[0]
            username = slugify(username)

            original_username = username
            i = 1 
            while self.model.objects.filter(username=username).exists():
                username = f"{original_username}{i}"
                i += 1

        user = self.model(email=email, phone_number=phone_number, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, phone_number, password=None, **extra_fields):
        return self._create_user(email, phone_number, password, **extra_fields)
    def create_superuser(self, email, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, phone_number, password, **extra_fields)
    
class CategoryManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

class PostManager(models.Manager):
    def published(self):
        return self.filter(status=PostStatus.PUBLISHED)
    
    def search(self, query):
        return self.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(summary__icontains=query)
        )

    def by_category(self, category_slug):
        return self.filter(categories__slug=category_slug)

    def by_author(self, author_id):
        return self.filter(author_id=author_id)

    def recent(self, days=30):
        return self.filter(
            created_at__gte=timezone.now() - timedelta(days=days)
        )

class CommentManager(models.Manager):
    def approved(self):
        return self.filter(status=CommentStatus.APPROVED)

    def pending(self):
        return self.filter(status=CommentStatus.PENDING)

    def by_post(self, post):
        return self.filter(post=post, parent__isnull=True)

    def replies(self, comment):
        return self.filter(parent=comment)

    
