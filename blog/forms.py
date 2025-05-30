from django import forms
from allauth.account.forms import SignupForm
class CustomSignupForm(SignupForm):
    phone_number = forms.CharField(max_length=15, label='Phone Number')
    
    def save(self, request):
        user = super(CustomSignupForm,self).save(request)
        user.phone_number = self.cleaned_data['phone_number']
        user.save()
        return user
        