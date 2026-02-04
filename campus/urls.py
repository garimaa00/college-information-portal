# from django import views
# from django.urls import path
# from .views import student_dashboard, teacher_dashboard, mark_attendance, mark_teacher_attendance, add_assignment, admin_dashboard, manage_courses, set_exam_dates, send_notifications, update_seats, post_event, alert_fee_dues

# urlpatterns = [
#     #student and teacher dashboard
#     path('student/', student_dashboard, name='student_dashboard'),
#     path('teacher/', teacher_dashboard, name='teacher_dashboard'),
    
#     #attendance-related
#     path('teacher/attendance/', mark_attendance, name='mark_attendance'),
#     path('teacher/teacher_attendance/', mark_teacher_attendance, name='mark_teacher_attendance'),
#     path('teacher/add_assignment/', add_assignment, name='add_assignment'),
 
#   #admin dashboard and management
#     path('admin/', admin_dashboard, name='admin_dashboard'),
#     path('admin/manage_courses/', manage_courses, name='manage_courses'),
#     path('admin/set_exam_dates/', set_exam_dates, name='set_exam_dates'),
#     path('admin/send_notifications/', send_notifications, name='send_notifications'),
#     path('admin/update_seats/', update_seats, name='update_seats'),
#     path('admin/post_event/', post_event, name='post_event'),
#     path('admin/alert_fee_dues/', alert_fee_dues, name='alert_fee_dues'),
   
#     # Attendance-related paths
#     path('mark/', views.mark_attendance, name='mark_attendance'),
#     path('teacher/mark/', views.mark_teacher_attendance, name='mark_teacher_attendance'),
#     path('view/', views.view_attendance, name='view_attendance', kwargs={'role': 'student'}),
#     path('view/<str:role>/', views.view_attendance, name='view_attendance_by_role'),
   
#     # Existing campus paths
#     path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
#     path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
#     path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
#     path('bim-course-details/', views.bim_course_details, name='bim_course_details'),
#     # Add other paths as needed (e.g., manage_courses, set_exam_dates)
#     path('manage-courses/', views.manage_courses, name='manage_courses'),
#     path('set-exam-dates/', views.set_exam_dates, name='set_exam_dates'),
#     path('send-notifications/', views.send_notifications, name='send_notifications'),
#     path('update-seats/', views.update_seats, name='update_seats'),
#     path('post-event/', views.post_event, name='post_event'),
#     path('alert-fee-dues/', views.alert_fee_dues, name='alert_fee_dues'),
#     path('add-assignment/', views.add_assignment, name='add_assignment'),


# ]



from django.urls import path
from .views import student_dashboard, teacher_dashboard, mark_attendance, mark_teacher_attendance, add_assignment, admin_dashboard, manage_courses, set_exam_dates, send_notifications, update_seats, post_event, alert_fee_dues, view_attendance, bim_course_details, submit_assignment, assignment_detail, view_exam_dates, view_events, view_notifications, check_fee_status, view_my_attendance, select_semester, view_submissions, delete_notification, approve_user, edit_assignment, delete_assignment, list_assignments

urlpatterns = [
    path('select_semester/', select_semester, name='select_semester'),
    # Student and Teacher Dashboards
    path('student/', student_dashboard, name='student_dashboard'),
    path('teacher/', teacher_dashboard, name='teacher_dashboard'),
    
    # Attendance-related paths
    path('teacher/attendance/', mark_attendance, name='mark_attendance'),
    path('teacher/teacher_attendance/', mark_teacher_attendance, name='mark_teacher_attendance'),
    path('view/', view_attendance, name='view_attendance', kwargs={'role': 'student'}),
    path('view/<str:role>/', view_attendance, name='view_attendance_by_role'),
    
    # Teacher-specific
    path('teacher/add_assignment/', add_assignment, name='add_assignment'),
    path('teacher/assignments/', list_assignments, name='list_assignments'),
    path('teacher/assignment/<int:pk>/edit/', edit_assignment, name='edit_assignment'),
    path('teacher/assignment/<int:pk>/delete/', delete_assignment, name='delete_assignment'),
    path('teacher/assignment/<int:pk>/submissions/', view_submissions, name='view_submissions'),

    # Student-specific
    path('student/attendance/', view_my_attendance, name='view_my_attendance'),
    path('student/submit_assignment/', submit_assignment, name='submit_assignment'),
    path('student/assignment/<int:pk>/', assignment_detail, name='assignment_detail'),
    path('student/exams/', view_exam_dates, name='view_exam_dates'),
    path('student/events/', view_events, name='view_events'),
    path('student/notifications/', view_notifications, name='view_notifications'),
    path('student/fees/', check_fee_status, name='check_fee_status'),


    
    # Admin Dashboards and Management
    path('admin/', admin_dashboard, name='admin_dashboard'),
    path('admin/manage_courses/', manage_courses, name='manage_courses'),
    path('admin/set_exam_dates/', set_exam_dates, name='set_exam_dates'),
    path('admin/send_notifications/', send_notifications, name='send_notifications'),
    path('admin/delete_notification/<int:pk>/', delete_notification, name='delete_notification'),
    path('admin/update_seats/', update_seats, name='update_seats'),
    path('admin/post_event/', post_event, name='post_event'),
    path('admin/alert_fee_dues/', alert_fee_dues, name='alert_fee_dues'),

    # Additional Paths
    path('bim-course-details/', bim_course_details, name='bim_course_details'),
    path('admin/approve_user/<int:user_id>/', approve_user, name='approve_user'),
]