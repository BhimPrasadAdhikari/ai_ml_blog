from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.urls import reverse

from django.db.models import CharField, ImageField, DateTimeField,BooleanField, TextField, EmailField,ForeignKey, ManyToManyField
from markdownx.models import MarkdownxField



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

class Category(models.Model):
    name = CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})
    
class Post(models.Model):
    """
    Model to store blog posts for the AI/ML blog.
    """
    STATUS_CHOICE = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )
    title = CharField(max_length=200)
    slug = CharField(max_length=255, unique=True, blank=True)
    summary = TextField(max_length=500, help_text="A short summary of the post")
    content = MarkdownxField()
    image = ImageField(upload_to='', blank=True, null=True)
    author = ForeignKey(get_user_model(),
                        on_delete=models.CASCADE,
                        related_name='posts')
    categories = ManyToManyField(Category, 
                                 related_name='posts',
                                 blank=True)
    tags = CharField(max_length=250, 
                     blank=True, 
                     help_text="comma-separated tags")
    status = CharField(max_length=10, 
                       choices=STATUS_CHOICE,
                       default='draft')
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    published_at = DateTimeField(blank=True, null=True)
    
    
    
    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})
    
    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    def __str__(self):
        return self.title
    
    class Meta: 
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['-published_at','-created_at']
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
class Comment(models.Model):
    """
    Model to store comments on blog posts.
    """
    post = models.ForeignKey(Post, 
                           on_delete=models.CASCADE,
                           related_name='comments')
    author = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self',
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True,
                             related_name='replies')

    is_edited = models.BooleanField(default=False)
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_comments'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        permissions = [
            ("can_moderate_comments", "Can moderate comments"),
        ]
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
    
    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment"""
        return self.parent is not None
    
    @property
    def get_replies(self):
        """Get all replies to this comment"""
        return self.replies.all()
    
    @property
    def get_parent_comment(self):
        """Get the parent comment if this is a reply"""
        return self.parent if self.is_reply else None

        
class PostInteraction(models.Model):
    """
    Model to store interactions with blog posts.
    """
    VOTE_CHOICES = (
        ('up', 'Upvote'),
        ('down', 'Downvote'),
        (None, 'No vote')

    )
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='interactions')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='post_interactions')
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES, default=None)
    watch_time = models.IntegerField(default=0)
    last_read_position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ['post', 'user']
        ordering = ['-created_at']
        verbose_name = "Post Interaction"
        verbose_name_plural = "Post Interactions"

    def __str__(self):
        return f'{self.user.username} voted {self.vote} on {self.post.title}'

    @property
    def is_upvote(self):
        return self.vote == 'up'
    
    @property
    def is_downvote(self):
        return self.vote == 'down'

    def get_upvotes(self):
        return self.interactions.filter(vote_type='up').count()
    
    def get_downvotes(self):
        return self.interactions.filter(vote_type='down').count()
    
    def get_vote_count(self):
        return self.get_upvotes() - self.get_downvotes()

    def get_user_vote(self, user):
        if not user.is_authenticated:
            return None
        try:
            interaction = self.interactions.get(user=user)
            return interaction.vote_type
        except PostInteraction.DoesNotExist:
            return None
            

    
    


    
        
        
        
        
        
        
        
        
        
    
