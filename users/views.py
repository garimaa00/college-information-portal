from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import login, get_user_model, authenticate
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

User = get_user_model()



def register_view(request):
    from .forms import CustomUserCreationForm  # Lazy import
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Registration successful! Please log in with your credentials.")
            if user.role == 'teacher':
                return redirect('teacher_login')
            elif user.role == 'student':
                return redirect('student_login')
            else:
                return redirect('login')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Admin Login View
@method_decorator(sensitive_post_parameters('password'), name='dispatch')
class AdminLoginView(LoginView):
    template_name = 'users/admin_login.html'
    
    def get_form_class(self):
        from .forms import AdminLoginForm
        return AdminLoginForm
    
    def form_valid(self, form):
        user = form.get_user()
        # Strictly allow only the specific admin email from setup_admin.py
        if user.email != 'admin@shankerdev.edu':
             messages.error(self.request, "Access Denied. Only the main administrator can login here.")
             return self.form_invalid(form)
             
        if user.role != 'admin' and not user.is_superuser:
             messages.error(self.request, "Access Denied. Admins only.")
             return self.form_invalid(form)
             
        login(self.request, user)
        self.request.session['role'] = 'admin'
        messages.success(self.request, "Welcome, Admin.")
        return redirect('admin_dashboard')

# Student Login View
@method_decorator(sensitive_post_parameters('password'), name='dispatch')
class StudentLoginView(LoginView):
    template_name = 'users/student_login.html'
    
    def get_form_class(self):
        from .forms import CustomAuthenticationForm
        return CustomAuthenticationForm

    def get_initial(self):
        initial = super().get_initial()
        initial['role'] = 'student'
        return initial

    def form_valid(self, form):
        user = form.get_user()
        role = form.cleaned_data.get('role')
        if user.role != 'student':
             messages.error(self.request, "Access Denied. Students only.")
             return self.form_invalid(form)
             
        login(self.request, user)
        # Force session role to match user role (student)
        self.request.session['role'] = 'student' 
        messages.success(self.request, "Welcome, Student.")
        return redirect('select_semester') # Or student_dashboard

# Teacher Login View
@method_decorator(sensitive_post_parameters('password'), name='dispatch')
class TeacherLoginView(LoginView):
    template_name = 'users/teacher_login.html'

    def get_form_class(self):
        from .forms import CustomAuthenticationForm
        return CustomAuthenticationForm

    def get_initial(self):
        initial = super().get_initial()
        initial['role'] = 'teacher'
        return initial
    
    def form_valid(self, form):
        user = form.get_user()
        if user.role != 'teacher':
             messages.error(self.request, "Access Denied. Teachers only.")
             return self.form_invalid(form)
             
        login(self.request, user)
        self.request.session['role'] = 'teacher'
        messages.success(self.request, "Welcome, Teacher.")
        return redirect('teacher_dashboard')

def login_selection(request):
    return render(request, 'users/login_selection.html')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login_selection')

# Admin-only Add User View
from campus.views import admin_required

@login_required
@admin_required
def add_user(request):
    from .forms import AddUserForm
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()
            
            # Send Email
            try:
                send_mail(
                    'Your ShankerDev Campus Credentials',
                    f'Hello {user.first_name},\n\nYour account has been created.\n\nRole: {user.role}\nEmail: {user.email}\nPassword: {password}\n\nPlease login and change your password.',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, f"User {user.email} created and credentials emailed.")
            except Exception as e:
                messages.warning(request, f"User created but failed to send email: {e}")
                
            return redirect('admin_dashboard')
    else:
        form = AddUserForm()
    return render(request, 'users/add_user.html', {'form': form})