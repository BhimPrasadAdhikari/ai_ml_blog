from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.db.models import (
    CharField,
    TextField,
    ImageField,
    ForeignKey,
    ManyToManyField,
    DateTimeField,
    BooleanField,
    EmailField,
    SET_NULL,
    IntegerField,
    URLField,
    OneToOneField,
    CASCADE,
    TextChoices,
    Sum,
    Index,
    SET,
)
from django.contrib.auth.base_user import BaseUserManager
from .validators import validate_image_size, validate_image_dimensions, validate_image_extension
from .managers import CustomUserManager
from PIL import Image
import os
from .constants import PostStatus, CommentStatus, VoteType, SharePlatform, PostInteractionType, MAX_IMAGE_SIZE, MAX_IMAGE_DIMENSION, MAX_THUMBNAIL_DIMENSION, VALID_IMAGE_EXTENSIONS, VALID_VIDEO_EXTENSIONS, VALID_AUDIO_EXTENSIONS, VALID_DOCUMENT_EXTENSIONS, VALID_ARCHIVE_EXTENSIONS, VALID_CODE_EXTENSIONS, VALID_TEXT_EXTENSIONS
from .mixins import TimestampMixin, SlugMixin, ImageProcessingMixin
class CustomUser(AbstractUser):
   
    phone_number = PhoneNumberField(unique=True, null=False, blank=False)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email

class Category(SlugMixin, models.Model):
    name = CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

class Post(SlugMixin, TimestampMixin, ImageProcessingMixin, models.Model):
    """
    Model to store blog posts for the AI/ML blog.
    """
    STATUS_CHOICE = PostStatus.choices
    title = CharField(max_length=200)
    summary = TextField(max_length=500, help_text="A short summary of the post")
    content = TextField()
    image = ImageField(upload_to='',
                       blank=True, 
                       null=True,
                       validators=[
                           validate_image_size,
                           validate_image_dimensions,
                           validate_image_extension
                       ])
    author = ForeignKey(get_user_model(),
                        on_delete=CASCADE,
                        related_name='posts')
    categories = ManyToManyField(Category, 
                                 related_name='posts',
                                 blank=True)
    tags = CharField(max_length=250, 
                     blank=True, 
                     help_text="comma-separated tags")
    status = CharField(max_length=10, 
                       choices=STATUS_CHOICE,
                       default=PostStatus.DRAFT)
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
        super().save(*args, **kwargs)
        if self.image:
            self.process_image(self.image)
    
    def get_upvotes(self):
        """Get the number of upvotes for this post"""
        return self.interactions.filter(vote_type=VoteType.UP).count()

    def get_downvotes(self):
        """Get the number of downvotes for this post"""
        return self.interactions.filter(vote_type=VoteType.DOWN).count()

    def get_vote_count(self):
        """Get the total vote count (upvotes - downvotes)"""
        return self.get_upvotes() - self.get_downvotes()

    def get_user_vote(self, user):
        """Get the user's vote for this post"""
        if not user.is_authenticated:
            return None
        try:
            interaction = self.interactions.get(user=user)
            return interaction.vote_type
        except PostInteraction.DoesNotExist:
            return None

class Comment(TimestampMixin, models.Model):
    """
    Model to store comments on blog posts.
    """
    post = ForeignKey(Post, 
                           on_delete=CASCADE,
                           related_name='comments')
    author = ForeignKey(get_user_model(),
                             on_delete=CASCADE,
                             related_name='comments')
    content = TextField()
    parent = ForeignKey('self',
                             on_delete=CASCADE,
                             null=True,
                             blank=True,
                             related_name='replies')

    is_edited = BooleanField(default=False)
    
    STATUS_CHOICES = CommentStatus.choices
    status = CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=CommentStatus.PENDING
    )
    moderated_at = DateTimeField(null=True, blank=True)
    moderated_by = ForeignKey(
        get_user_model(),
        on_delete=SET_NULL,
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

        
class PostInteraction(TimestampMixin, models.Model):
    """
    Model to track user interactions with posts including votes and watch time.
    """
    post = ForeignKey(Post, 
                           on_delete=CASCADE,
                           related_name='interactions')
    user = ForeignKey(get_user_model(),
                           on_delete=CASCADE,
                           related_name='post_interactions')
    vote_type = CharField(
        max_length=10,
        choices=VoteType.choices,
        null=True,
        blank=True
    )
    watch_time = IntegerField(default=0)  # in seconds
    last_read_position = IntegerField(default=0)  # scroll position

    class Meta:
        unique_together = ['post', 'user']
        ordering = ['-created_at']
        verbose_name = "Post Interaction"
        verbose_name_plural = "Post Interactions"

    def __str__(self):
        return f"{self.user.username}'s interaction with {self.post.title}"

    @property
    def is_upvote(self):
        return self.vote_type == VoteType.UP
    
    @property
    def is_downvote(self):
        return self.vote_type == VoteType.DOWN

    def get_upvotes(self):
        return self.interactions.filter(vote_type=VoteType.UP).count()
    
    def get_downvotes(self):
        return self.interactions.filter(vote_type=VoteType.DOWN).count()
    
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
            

    
class PostWatchTime(TimestampMixin, models.Model):
    """
    Model to track user watch time for a post.
    """
    post = ForeignKey(Post, 
                             on_delete=CASCADE,
                             related_name='watch_times')
    user = ForeignKey(get_user_model(),
                             on_delete=CASCADE,
                             related_name='post_watch_times')
    watch_time = IntegerField(default=0)   
    class Meta:
        unique_together = ['post', 'user']
        indexes = [
            Index(fields=['post', 'user']),
            Index(fields=['updated_at']),
        ]


    def __str__(self):
        return f"{self.user.username}'s watch time for {self.post.title} is {self.watch_time} seconds"

    

class PostShare(TimestampMixin, models.Model):
    SHARE_PLATFORMS = SharePlatform.choices
    
    post = ForeignKey(Post, on_delete=CASCADE, related_name='shares')
    platform = CharField(max_length=20, choices=SHARE_PLATFORMS)
    shared_by = ForeignKey(get_user_model(), on_delete=SET_NULL, null=True, blank=True)
   
    class Meta:
        indexes = [
            Index(fields=['post', 'platform']),
            Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.post.title} shared on {self.platform}"

    
class PostBookmark(TimestampMixin, models.Model):
    """Model for user bookmarks/favorites"""
    post = ForeignKey(Post, on_delete=CASCADE, related_name='bookmarks')
    user = ForeignKey(get_user_model(), on_delete=CASCADE, related_name='bookmarked_posts')
    notes = TextField(blank=True, help_text="Personal notes about this post")

    class Meta:
        unique_together = ['post','user']
        verbose_name = "Post Bookmark"
        verbose_name_plural = "Post Bookmarks"

    def __str__(self):
        return f"{self.user.username} bookmarked {self.post.title}"


class PostRating(TimestampMixin, models.Model):
    post = ForeignKey(Post, on_delete=CASCADE, related_name='ratings' )
    user = ForeignKey(get_user_model(), on_delete=CASCADE, related_name='post_ratings')
    rating = IntegerField(choices=[ (i,i)for i in range(1,6)], default=0)

    class Meta:
        unique_together = ['post', 'user']
        verbose_name = "Post Rating"
        verbose_name_plural = "Post Ratings"
        
    def __str__(self):
        return f"{self.user.username} rated {self.post.title} {self.rating}"
    
    

class UserProfile(TimestampMixin, models.Model):
    user = OneToOneField(get_user_model(), on_delete=CASCADE, related_name='profile')
    bio = TextField(max_length=500, blank=True)
    profile_picture = ImageField(upload_to='profile_pictures/', blank=True, null=True)
    website = URLField(max_length=200, blank=True)
    location = CharField(max_length=100, blank=True)
    github = URLField(max_length=200, blank=True)
    twitter = URLField(max_length=200, blank=True)
    linkedin = URLField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_absolute_url(self):
        return reverse('profile_detail', kwargs={'username': self.user.username})

    @property
    def total_posts(self):
        return self.user.posts.filter(status=PostStatus.PUBLISHED).count()

    @property
    def total_comments(self):
        return self.user.comments.filter(status=CommentStatus.APPROVED).count()

    @property
    def total_upvotes_received(self):
        return PostInteraction.objects.filter(
            post__author=self.user,
            vote_type=VoteType.UP
        ).count()

    @property
    def total_watch_time(self):
        return PostWatchTime.objects.filter(
            post__author=self.user
        ).aggregate(total=Sum('watch_time'))['total'] or 0

    @property
    def total_shares(self):
        return PostShare.objects.filter(
            post__author=self.user
        ).count()

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"



class EmailSubscription(TimestampMixin, models.Model):
    """
    Model to store email subscriptions for the blog.
    """
    email = EmailField(unique=True)
    first_name = CharField(max_length=100, blank=True)
    last_name = CharField(max_length=100, blank=True)
    is_active = BooleanField(default=True)
    subscribed_at = DateTimeField(auto_now_add=True)
    unsubscribed_at = DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Email Subscription"
        verbose_name_plural = "Email Subscriptions"
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email
    
    def unsubscribe(self):
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()

    
class Newsletter(TimestampMixin, models.Model):
    """
    Model for newsletter campaigns
    """
    subject = CharField(max_length=200)
    content = TextField()
    sent_at = DateTimeField(null=True, blank=True)
    is_sent = BooleanField(default=False)
    sent_count = IntegerField(default=0)

    class Meta:
        verbose_name = "Newsletter"
        verbose_name_plural = "Newsletters"
        ordering = ['-created_at']

    def __str__(self):
        return self.subject






