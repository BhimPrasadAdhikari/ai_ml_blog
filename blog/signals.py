from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Import here to avoid circular import
        from .models import UserProfile
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=get_user_model())
def save_user_profile(sender, instance, created, **kwargs):
    # Import here to avoid circular import
    from .models import UserProfile
    if not created:
        # Get or create profile for existing users
        UserProfile.objects.get_or_create(user=instance)

