from django import forms
from .models import Post, Comment, UserProfile
from allauth.account.forms import SignupForm
class CustomSignupForm(SignupForm):
    phone_number = forms.CharField(max_length=15, label='Phone Number')
    
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