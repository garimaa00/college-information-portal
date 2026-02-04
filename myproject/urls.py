# """
# URL configuration for myproject project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.2/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# from django.contrib import admin
# from django.urls import path, include
# from django.contrib.auth.views import LogoutView
# from django.views.generic.base import RedirectView
# from users.views import CustomLoginView, register_view
# from campus.views import student_dashboard, teacher_dashboard, admin_dashboard, bim_course_details

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('courses/', include('courses.urls')),
#     path('campus/', include('campus.urls')),  # All campus-related paths, including attendance
#     path('', RedirectView.as_view(url='/login/', permanent=False), name='home'),
#     path('login/', CustomLoginView.as_view(), name='login'),
#     path('logout/', LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
#     path('register/', register_view, name='register'),
#     path('student-dashboard/', student_dashboard, name='student_dashboard'),
#     path('teacher-dashboard/', teacher_dashboard, name='teacher_dashboard'),
#     path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
#     path('bim-course-details/', bim_course_details, name='bim_course_details'),
#     path('accounts/', include('django.contrib.auth.urls')),
#     #  path('attendance/', include('attendance.urls')),
# ]



from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.views.generic.base import RedirectView
from django.views.generic.base import RedirectView
from users.views import StudentLoginView, register_view, logout_view
from campus.views import student_dashboard, teacher_dashboard, admin_dashboard, bim_course_details
from myproject.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('courses/', include('courses.urls')),
    path('campus/', include('campus.urls')),  # All campus-related paths, including attendance
    path('users/', include('users.urls')), # Include users URLs
    path('', home_view, name='home'),
    path('login/', StudentLoginView.as_view(), name='login'),  # Student login as default
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('student-dashboard/', student_dashboard, name='student_dashboard'),
    path('teacher-dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('bim-course-details/', bim_course_details, name='bim_course_details'),
    path('attendance/', include('attendance.urls')),  # Added attendance URLs
    # Exclude default login URL to avoid conflict with CustomLoginView
    path('accounts/', include(([], 'django.contrib.auth'), namespace='accounts')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)