
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('mark/', views.mark_attendance, name='mark_attendance'),
#     path('teacher/mark/', views.mark_teacher_attendance, name='mark_teacher_attendance'),
# ]

from django.urls import path
from . import views

app_name = 'attendance'  # Namespace for URL reversing

urlpatterns = [
    path('', views.attendance_list, name='attendance_list'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('teacher/mark/', views.mark_teacher_attendance, name='mark_teacher_attendance'),
    path('view/', views.view_attendance, name='view_attendance', kwargs={'role': 'student'}),
    path('view/<str:role>/', views.view_attendance, name='view_attendance_by_role'),
]