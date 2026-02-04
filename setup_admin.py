import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from users.models import CustomUser

def setup_admin():
    email = "admin@shankerdev.edu"
    password = "adminpassword123"
    
    if not CustomUser.objects.filter(email=email).exists():
        print(f"Creating admin user: {email}")
        CustomUser.objects.create_superuser(email=email, password=password, role='admin')
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")

if __name__ == "__main__":
    setup_admin()
