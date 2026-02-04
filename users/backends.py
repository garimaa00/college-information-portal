# from django.contrib.auth.backends import ModelBackend
# from .models import CustomUser

# class CustomBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         try:
#             user = CustomUser.objects.get(email=username) or CustomUser.objects.get(phone_number=username) or CustomUser.objects.get(username=username)
#             if user.check_password(password):
#                 return user
#         except CustomUser.DoesNotExist:
#             return None


# from django.contrib.auth.backends import ModelBackend
# from .models import CustomUser
# from django.contrib.auth import get_user_model

# class CustomBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         try:
#             user = CustomUser.objects.get(email=username) or CustomUser.objects.get(phone_number=username)
#             if user.check_password(password):
#                 return user
#         except CustomUser.DoesNotExist:
#             return None
        
# class EmailBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         UserModel = get_user_model()
#         try:
#             user = UserModel.objects.get(email=username)  # Assuming username is email
#             if user.check_password(password):
#                 return user
#         except UserModel.DoesNotExist:
#             return None

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(phone_number=username)
            except User.DoesNotExist:
                return None
        if user.check_password(password):
            return user
        return None