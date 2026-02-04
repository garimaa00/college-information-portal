
from django.urls import path
from django.urls import path
from .views import AdminLoginView, StudentLoginView, TeacherLoginView, add_user, login_selection, register_view

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', StudentLoginView.as_view(), name='login'), # Replaced old login with Student Login
    path('admin-login/', AdminLoginView.as_view(), name='admin_login'),
    path('student-login/', StudentLoginView.as_view(), name='student_login'),
    path('teacher-login/', TeacherLoginView.as_view(), name='teacher_login'),
    path('login-selection/', login_selection, name='login_selection'),
    path('add-user/', add_user, name='add_user'),
]