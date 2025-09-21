# blog/adapter.py
from allauth.account.adapter import DefaultAccountAdapter
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomAccountAdapter(DefaultAccountAdapter):

    def clean_email(self, email):
        """
        Only check email uniqueness for signup, not for password reset.
        """
        email = super().clean_email(email)
        
        # Only enforce during signup
        if getattr(self, 'is_signup', False):
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError(
                    "This email is already used. Please try a different one."
                )
        
        return email

    def is_email_taken(self, email):
        """
        Deprecated, you can remove this method or keep for future use.
        """
        return User.objects.filter(email__iexact=email).exists()
