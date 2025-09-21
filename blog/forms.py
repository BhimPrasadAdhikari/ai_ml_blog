from django import forms
from .models import Post, Comment, UserProfile, EmailSubscription, Newsletter, PostBookmark, PostRating
from allauth.account.forms import SignupForm
from phonenumber_field.formfields import PhoneNumberField

class CustomSignupForm(SignupForm):
    phone_number = PhoneNumberField(
        label='Phone Number',
        required = False,
        error_messages={
            'invalid': 'Enter a valid phone number (e.g. +1234567890)',
            'required': 'Phone number is required'
        }
    )
    
    def save(self, request):
        user = super(CustomSignupForm,self).save(request)
        user.phone_number = self.cleaned_data['phone_number']
        user.save()
        return user

class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
    class Media:
        css = {'all': ('https://unpkg.com/easymde/dist/easymde.min.css',)}
        js = (
            'https://unpkg.com/easymde/dist/easymde.min.js',
            'blog/js/easymde-init.js',  # Make sure this file exists in your static files
        )
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment...',
            })
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'website', 'location', 
                 'github', 'twitter', 'linkedin']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://your-website.com'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your location'
            }),
            'github': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/username'
            }),
            'twitter': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://twitter.com/username'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/username'
            }),
        }

class EmailSubscriptionForm(forms.ModelForm):
    class Meta:
        model = EmailSubscription
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
        }

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['subject', 'content']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

class PostBookmarkForm(forms.ModelForm):
    class Meta:
        model = PostBookmark
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add personal notes about this post...'}),
        }

class PostRatingForm(forms.ModelForm):
    class Meta:
        model = PostRating
        fields = ['rating']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
        }
        