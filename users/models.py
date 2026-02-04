# from django.contrib.auth.models import AbstractUser, BaseUserManager
# from django.db import models
# from django.core.exceptions import ValidationError
# from django.utils import timezone

# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         base_username = email.split('@')[0].replace('.', '_')
#         username = f"{base_username}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
#         while self.model.objects.filter(username=username).exists():
#             username = f"{base_username}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
#         user = self.model(email=email, username=username, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('role', 'admin')
#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')
#         if extra_fields.get('role') != 'admin':
#             raise ValueError('Superuser must have role=admin.')
#         return self.create_user(email, password, **extra_fields)

# class CustomUser(AbstractUser):
#     ROLE_CHOICES = (
#         ('student', 'Student'),
#         ('teacher', 'Teacher'),
#         ('admin', 'Admin'),
#     )
#     email = models.EmailField(unique=True)
#     phone_number = models.CharField(max_length=15, blank=True, null=True)
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

#     objects = CustomUserManager()

#     def __str__(self):
#         return self.username or self.email

#     def save(self, *args, **kwargs):
#         if self.email:
#             self.email = self.__class__.objects.normalize_email(self.email)
#         super().save(*args, **kwargs)

# class Task(models.Model):
#     teacher = models.ForeignKey(CustomUser, related_name='assigned_tasks', on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
#     students = models.ManyToManyField(CustomUser, related_name='received_tasks', limit_choices_to={'role': 'student'})
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     due_date = models.DateField()
#     completed = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.title} (Due: {self.due_date})"

# class Event(models.Model):
#     title = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     date = models.DateField(default=timezone.now)
#     time = models.TimeField(default=timezone.now().time)
#     location = models.CharField(max_length=200, blank=True)

#     def __str__(self):
#         return f"{self.title} on {self.date} at {self.time}"




from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def make_random_password(self, length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
        from django.utils.crypto import get_random_string
        return get_random_string(length, allowed_chars)
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        base_username = email.split('@')[0].replace('.', '_')
        username = f"{base_username}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
        while self.model.objects.filter(username=username).exists():
            username = f"{base_username}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('role') != 'admin':
            raise ValueError('Superuser must have role=admin.')
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_approved = models.BooleanField(default=False, help_text="Designates whether this user has been approved by an admin.")
    
    # username = None removed to allow standard AbstractUser username field

    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.username or self.email

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)
        super().save(*args, **kwargs)

class Task(models.Model):
    teacher = models.ForeignKey(CustomUser, related_name='assigned_tasks', on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    students = models.ManyToManyField(CustomUser, related_name='received_tasks', limit_choices_to={'role': 'student'})
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} (Due: {self.due_date})"

# Function to provide default time
def get_current_time():
    return timezone.now().time()

class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=get_current_time)  # Use the function name
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.title} on {self.date} at {self.time}"