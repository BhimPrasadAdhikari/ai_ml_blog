from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Try to fetch the user by email
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            try:
                # Try to fetch the user by phone number
                user = UserModel.objects.get(phone_number=username)
            except UserModel.DoesNotExist:
                return None
        if user.check_password(password):
            return user
        return None
