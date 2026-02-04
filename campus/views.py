from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import AssignmentForm, CourseForm, EventForm, ExamRoutineForm, FeeDueForm, NotificationForm, UpdateSeatsForm, SubmissionForm, SemesterSelectionForm
from .models import Attendance, Course, StudentProfile, TeacherProfile, ExamRoutine, FeeDue, Event, Assignment, TeacherAttendance, Subject, Faculty, Submission, UserNotificationTracker
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

def student_required(function):
    return user_passes_test(lambda u: u.role == 'student' and u.is_authenticated)(function)

def teacher_required(function):
    return user_passes_test(lambda u: u.role == 'teacher' and u.is_authenticated)(function)

def admin_required(function):
    return user_passes_test(lambda u: u.role == 'admin' and u.is_authenticated)(function)

@login_required
@student_required
def select_semester(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = SemesterSelectionForm(request.POST)
        if form.is_valid():
            profile.semester = form.cleaned_data['semester']
            profile.section = form.cleaned_data['section']
            profile.save()
            messages.success(request, f"Semester {profile.semester} and Section {profile.section} selected.")
            return redirect('student_dashboard')
    else:
        initial_data = {'semester': profile.semester, 'section': profile.section}
        form = SemesterSelectionForm(initial=initial_data)
    return render(request, 'campus/select_semester.html', {'form': form})

@login_required
@student_required
def student_dashboard(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if created:
        messages.info(request, "Welcome! Your student profile has been created.")

    # Check if section is set, if not redirect to selection (optional safety check)
    if not profile.section:
        return redirect('select_semester')

    attendance_percent = (profile.attended_days / profile.total_days * 100) if profile.total_days else 0
    if attendance_percent < 80:
        messages.warning(request, f"Low attendance: {attendance_percent:.1f}%. Contact your faculty.")
        try:
             send_mail(
                'Low Attendance Alert',
                f'Your attendance is {attendance_percent:.1f}%, below 80%. Contact your faculty.',
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=True,
            )
        except Exception:
             pass

    if profile:
        # Filter exams by subjects in the student's semester
        # Filter exams by subjects in the student's semester
        exams = ExamRoutine.objects.filter(subject__semester=profile.semester, date__gte=date.today()).order_by('date')
        fees = FeeDue.objects.filter(student=request.user, due_date__gte=date.today()).order_by('due_date')
        events = Event.objects.filter(date__gte=date.today()).order_by('date')
        # Show all future assignments for the student's semester
        assignments = Assignment.objects.filter(semester=profile.semester, due_date__gte=date.today()).order_by('due_date')
        subjects = Subject.objects.filter(semester=profile.semester, faculty=profile.faculty).order_by('name')
    else:
        exams = []
        fees = []
        events = []
        assignments = []
        subjects = []
    
    teachers_attendance = TeacherAttendance.objects.filter(date=date.today()).select_related('teacher').order_by('teacher__email')
    
    # Fetch recent notifications
    from .models import Notification
    from django.db.models import Q
    
    # Filter: 
    # 1. Targeted to user (recipient=user)
    # 2. Global (recipient=None AND semester=None)
    # 3. Semester specific (recipient=None AND semester=user_semester)
    
    semester_filter = Q(recipient=None, semester=profile.semester) if profile.semester else Q(recipient=None, semester__isnull=True)
    
    recent_notifications = Notification.objects.filter(
        Q(recipient=request.user) | (Q(recipient__isnull=True) & Q(semester__isnull=True)) | semester_filter,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).exclude(message__startswith='Seats updated').order_by('-created_at')

    return render(request, 'campus/student_dashboard.html', {
        'attendance_percent': attendance_percent,
        'exams': exams,
        'fees': fees,
        'events': events,
        'assignments': assignments,
        'subjects': subjects,
        'teachers_attendance': teachers_attendance,
        'profile': profile,
        'notifications': recent_notifications,
    })

@login_required
@teacher_required
def teacher_dashboard(request):
    try:
        from django.db.models import Count
        subjects = request.user.teacherprofile.subjects.all().order_by('name')
        assignments = Assignment.objects.filter(teacher=request.user).annotate(submission_count=Count('submission')).order_by('due_date')
    except TeacherProfile.DoesNotExist:
        messages.error(request, "Your teacher profile is not set up. Contact an admin.")
        subjects = []
        assignments = []
    
    # Filter notifications for this user or global
    from django.db.models import Q
    from .models import Notification
    recent_notifications = Notification.objects.filter(
        Q(recipient=None) | Q(recipient=request.user)
    ).exclude(created_by=request.user).exclude(message__startswith='Seats updated').order_by('-created_at')[:5]

    context = {
        'subjects': subjects,
        'assignments': assignments,
        'notifications': recent_notifications,
        'current_date': timezone.now(),
    }
    return render(request, 'campus/teacher_dashboard.html', context)
@login_required
@teacher_required
def mark_attendance(request):
    if request.method == 'POST':
        students = request.POST.getlist('students')
        if not students:
            messages.error(request, "No students selected.")
            return redirect('mark_attendance')
        try:
            for student_id in students:
                student = User.objects.get(id=student_id)
                # Ensure profile exists to prevent crash in signal and below
                profile, created_profile = StudentProfile.objects.get_or_create(user=student)
                
                status = request.POST.get(f'status_{student_id}')
                present = (status == 'present')
                
                attendance, created_attendance = Attendance.objects.update_or_create(
                    student=student,
                    teacher=request.user,
                    date=date.today(),
                    defaults={'present': present}
                )
                
                # Only update stats if this is a NEW attendance record for the day
                # Or if logic permits recalculation (existing logic is naive increment)
                if present:
                    profile.attended_days += 1
                profile.total_days += 1
                profile.save()
            messages.success(request, 'Attendance marked successfully.')
        except (User.DoesNotExist, StudentProfile.DoesNotExist) as e:
            messages.error(request, f"Error marking attendance: {str(e)}")
        return redirect('teacher_dashboard')
    students = User.objects.filter(role='student').order_by('email')
 
    return render(request, 'campus/mark_attendance.html', {'students': students})

# @login_required
# @teacher_required
# def mark_attendance(request):
#     if request.method == 'POST':
#         students = request.POST.getlist('students')
#         if not students:
#             messages.error(request, "No students selected.")
#             return redirect('mark_attendance')
#         try:
#             for student_id in students:
#                 student = User.objects.get(id=student_id)
#                 present = student_id in request.POST.getlist('present_students', [])
#                 Attendance.objects.update_or_create(
#                     student=student,
#                     teacher=request.user,
#                     date=date.today(),
#                     defaults={'present': present}
#                 )
#                 profile = StudentProfile.objects.get(user=student)
#                 if present:
#                     profile.attended_days += 1
#                 profile.total_days += 1
#                 profile.save()
#             messages.success(request, 'Attendance marked successfully.')
#         except (User.DoesNotExist, StudentProfile.DoesNotExist) as e:
#             messages.error(request, f"Error marking attendance: {str(e)}")
#         return redirect('teacher_dashboard')
#     students = User.objects.filter(role='student').order_by('email')
#     return render(request, 'campus/mark_attendance.html', {'students': students})

@login_required
@teacher_required
def mark_teacher_attendance(request):
    if request.method == 'POST':
        try:
            present_str = request.POST.get('present', 'True')
            present = present_str == 'True'
            if not TeacherAttendance.objects.filter(teacher=request.user, date=date.today()).exists():
                 TeacherAttendance.objects.create(
                    teacher=request.user,
                    date=date.today(),
                    present=present
                )
            else:
                TeacherAttendance.objects.filter(teacher=request.user, date=date.today()).update(present=present)
            messages.success(request, 'Attendance marked.')
        except Exception as e:
            messages.error(request, f"Error marking attendance: {str(e)}")
        return redirect('teacher_dashboard')
    return render(request, 'campus/mark_teacher_attendance.html')


@login_required
@teacher_required
def add_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = request.user
            assignment.save()
            # Send targeted notification to semester
            create_notification(
                f"New Assignment: {assignment.title} (Sem {assignment.semester})\n"
                f"Subject: {assignment.subject}\n"
                f"Due Date: {assignment.due_date}\n\n"
                f"Description: {assignment.description}",
                request.user,
                semester=assignment.semester
            )
            
            # Send email notifications to students
            from .email_utils import send_assignment_notification_email
            students = User.objects.filter(
                role='student',
                studentprofile__semester=assignment.semester
            )
            today = date.today()
            for student in students:
                if not UserNotificationTracker.objects.filter(user=student, notification_type='assignment', last_sent_date=today).exists():
                    try:
                        send_assignment_notification_email(student, assignment, request.user)
                        UserNotificationTracker.objects.update_or_create(
                            user=student,
                            notification_type='assignment',
                            defaults={'last_sent_date': today}
                        )
                    except Exception:
                        pass
            messages.success(request, 'Assignment added successfully.')
            return redirect('teacher_dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = AssignmentForm()
    return render(request, 'campus/add_assignment.html', {'form': form})

@login_required
@teacher_required
def view_submissions(request, pk):
    try:
        assignment = Assignment.objects.get(id=pk, teacher=request.user)
        submissions = Submission.objects.filter(assignment=assignment).order_by('-submitted_at')
    except Assignment.DoesNotExist:
        messages.error(request, "Assignment not found or unauthorized.")
        return redirect('teacher_dashboard')
    
    return render(request, 'campus/view_submissions.html', {'assignment': assignment, 'submissions': submissions})

@login_required
@teacher_required
def edit_assignment(request, pk):
    try:
        assignment = Assignment.objects.get(id=pk, teacher=request.user)
    except Assignment.DoesNotExist:
        messages.error(request, "Assignment not found or you don't have permission to edit it.")
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            updated_assignment = form.save(commit=False)
            updated_assignment.teacher = request.user
            updated_assignment.save()
            
            # Send notification about updated assignment
            create_notification(
                f"Assignment Updated: {updated_assignment.title} (Sem {updated_assignment.semester})\n"
                f"Subject: {updated_assignment.subject}\n"
                f"New Due Date: {updated_assignment.due_date}\n\n"
                f"Description: {updated_assignment.description}",
                request.user,
                semester=updated_assignment.semester
            )
            messages.success(request, 'Assignment updated successfully.')
            return redirect('teacher_dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = AssignmentForm(instance=assignment)
    
    return render(request, 'campus/edit_assignment.html', {'form': form, 'assignment': assignment})

@login_required
@teacher_required
def delete_assignment(request, pk):
    try:
        assignment = Assignment.objects.get(id=pk, teacher=request.user)
    except Assignment.DoesNotExist:
        messages.error(request, "Assignment not found or you don't have permission to delete it.")
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        assignment_title = assignment.title
        assignment_semester = assignment.semester
        assignment.delete()
        
        # Send notification about deleted assignment
        create_notification(
            f"Assignment Deleted: {assignment_title} (Sem {assignment_semester})\n"
            f"This assignment has been removed by the teacher.",
            request.user,
            semester=assignment_semester
        )
        messages.success(request, f'Assignment "{assignment_title}" deleted successfully.')
        return redirect('teacher_dashboard')
    
    return render(request, 'campus/delete_assignment.html', {'assignment': assignment})

@login_required
@teacher_required
def list_assignments(request):
    """View all assignments created by the teacher"""
    try:
        from django.db.models import Count
        assignments = Assignment.objects.filter(teacher=request.user).annotate(
            submission_count=Count('submission')
        ).order_by('-due_date')
    except Exception as e:
        messages.error(request, "Error loading assignments.")
        assignments = []
    
    return render(request, 'campus/list_assignments.html', {'assignments': assignments})

@login_required
@admin_required
def admin_dashboard(request):
    try:
        courses = Course.objects.all().order_by('name')  # Use model directly for consistency
    except Exception:
        courses = []
        messages.error(request, "Could not load courses. Check database.")
    
    # Get statistics
    total_students = User.objects.filter(role='student').count()
    total_teachers = User.objects.filter(role='teacher').count()
    events = Event.objects.filter(date__gte=date.today()).order_by('date')
    active_events = events.count()
    pending_users = User.objects.filter(is_approved=False).order_by('-date_joined')
    
    return render(request, 'campus/admin_dashboard.html', {
        'courses': courses,
        'events': events,
        'pending_users': pending_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'active_events': active_events,
        'current_time': timezone.now(),
    })



# Helper to create notifications
def create_notification(message, user=None, recipient=None, semester=None):
    from .models import Notification
    Notification.objects.create(message=message, created_by=user, recipient=recipient, semester=semester)

# ... (Admin views remain similar, using default recipient=None)

@login_required
@admin_required
def alert_fee_dues(request):
    if request.method == 'POST':
        form = FeeDueForm(request.POST)
        if form.is_valid():
            fee_due = form.save()
            create_notification(
                f"Fee Alert: You have a fee due of {fee_due.amount} by {fee_due.due_date}", 
                request.user, 
                recipient=fee_due.student
            )
            
            # Send email notification
            from .email_utils import send_fee_reminder_email
            today = date.today()
            student = fee_due.student
            if not UserNotificationTracker.objects.filter(user=student, notification_type='fee_reminder', last_sent_date=today).exists():
                try:
                    send_fee_reminder_email(student, fee_due.amount, fee_due.due_date)
                    UserNotificationTracker.objects.update_or_create(
                        user=student,
                        notification_type='fee_reminder',
                        defaults={'last_sent_date': today}
                    )
                except Exception:
                    pass
                
            messages.success(request, 'Fee due alert sent successfully.')
            return redirect('admin_dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = FeeDueForm()
    return render(request, 'campus/alert_fee_dues.html', {'form': form})

@login_required
@admin_required
def manage_courses(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            create_notification(f"New course added: {course.name}\n\n{course.description}\nDuration: {course.duration}", request.user)
            messages.success(request, 'Course managed successfully.')
            return redirect('admin_dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CourseForm()
    return render(request, 'campus/manage_courses.html', {'form': form})

@login_required
@admin_required
def set_exam_dates(request):
    if request.method == 'POST':
        form = ExamRoutineForm(request.POST, request.FILES)
        if form.is_valid():
            exam = form.save()
            title = exam.title if exam.title else f"Routine for Semester {exam.semester}"
            create_notification(f"Exam Routine Uploaded: {title}", request.user, semester=exam.semester)
            
            messages.success(request, 'Exam routine updated successfully.')
            return redirect('admin_dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = ExamRoutineForm()
    return render(request, 'campus/set_exam_dates.html', {'form': form})

@login_required
@admin_required
def delete_notification(request, pk):
    from .models import Notification
    notification = Notification.objects.get(id=pk)
    if notification.created_by == request.user:
        notification.delete()
        messages.success(request, "Notification deleted.")
    else:
        messages.error(request, "You can only delete notifications you created.")
    return redirect('send_notifications')

@login_required
@admin_required
def send_notifications(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            recipient_type = form.cleaned_data['recipient_type']
            semester = form.cleaned_data.get('semester')
            
            recipients = []
            if recipient_type == 'all_students':
                recipients = User.objects.filter(role='student')
            elif recipient_type == 'all_students_teachers':
                recipients = User.objects.filter(role__in=['student', 'teacher'])
            elif recipient_type == 'specific_semester':
                 if not semester:
                     messages.error(request, "Please specify a semester.")
                     return render(request, 'campus/send_notifications.html', {'form': form})
                 # Create one notification for the semester
                 create_notification(f"Announcement (Sem {semester}): {subject}\n\n{message}", request.user, semester=semester)
                 messages.success(request, f'Notification sent to Semester {semester}.')
                 return redirect('send_notifications')
            else:
                recipients = form.cleaned_data['recipients']
                if not recipients:
                     messages.error(request, "Please select at least one recipient.")
                     return render(request, 'campus/send_notifications.html', {'form': form})

            for user in recipients:
                # Send Mail
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=True,
                )
             
            if recipient_type == 'all_students_teachers':
                 create_notification(f"Admin Announcement: {subject}\n\n{message}", request.user, recipient=None) # Global
            else:
                 # Loop for specific or all_students
                 filtered_msg = f"Admin Message: {subject}\n\n{message}"
                 for user in recipients:
                     create_notification(filtered_msg, request.user, recipient=user)

            messages.success(request, 'Notifications sent successfully.')
            return redirect('send_notifications')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = NotificationForm()
    
    # Fetch notifications sent by this admin
    from .models import Notification
    sent_notifications = Notification.objects.filter(created_by=request.user).order_by('-created_at')
    
    return render(request, 'campus/send_notifications.html', {'form': form, 'sent_notifications': sent_notifications})

@login_required
@admin_required
def update_seats(request):
    if request.method == 'POST':
        form = UpdateSeatsForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            course.available_seats = form.cleaned_data['available_seats']
            course.save()
            messages.success(request, 'Seats updated successfully.')
            return redirect('admin_dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UpdateSeatsForm()
    return render(request, 'campus/update_seats.html', {'form': form})

@login_required
@admin_required
def post_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            create_notification(f"New Event: {event.title} on {event.date}\n\n{event.description}", request.user)
            messages.success(request, 'Event posted successfully.')
            return redirect('admin_dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = EventForm()
    return render(request, 'campus/post_event.html', {'form': form})



# @login_required
# def bim_course_details(request):
#     try:
#         from .models import Course  # Lazy import to avoid circular issues
#         bim_course = Course.objects.filter(name__icontains='bim').first()
#         context = {
#             'course_info': {
#                 'title': bim_course.name if bim_course else 'Bachelor in Information Management (BIM)',
#                 'description': bim_course.description if bim_course else 'A 4-year program focusing on IT and management skills.',
#                 'duration': bim_course.duration if bim_course else '4 years',
#                 'location': bim_course.location if bim_course else 'Putalisadak, Kathmandu, Nepal'
#             }
#         }
#     except Exception as e:
#         messages.error(request, f"Error loading course details: {str(e)}")
#         context = {
#             'course_info': {
#                 'title': 'Bachelor in Information Management (BIM)',
#                 'description': 'A 4-year program focusing on IT and management skills.',
#                 'duration': '4 years',
#                 'location': 'Putalisadak, Kathmandu, Nepal'
#             }
#         }
#     return render(request, 'campus/bim_course_details.html', context)
def bim_course_details(request):
    # Fetch BIM course info
    bim_course = Course.objects.filter(name__iexact='BIM').first()
    if not bim_course:
        bim_course = Course.objects.filter(name__icontains='bim').first()

    course_info = {
        'title': 'Bachelor in Information Management (BIM)',
        'description': 'A 4-year program focusing on IT and management skills.It has 72 credit hours of information technology courses, 27 credit hours of management courses and 27 credit hours of analytical and support course.',
        'duration': '4 Years(8 Semesters)',
        'location': 'Putalisadak, Kathmandu, Nepal',
        'additional_info': getattr(bim_course, 'additional_info', '') if bim_course else '',
    }

    # Fetch BIM subjects from database
    subjects = Subject.objects.filter(faculty__name__icontains='BIM').order_by('semester', 'name')
    
    # Group by semester
    bim_subjects = {}
    for subject in subjects:
        if subject.semester not in bim_subjects:
            bim_subjects[subject.semester] = []
        bim_subjects[subject.semester].append(subject.name)
    
    # Sort by semester
    bim_subjects = dict(sorted(bim_subjects.items()))

    # Hardcoded fee structure as per user requirement
    fee_structure = {2079: 475000, 2080: 500000, 2081: 525000, 2082: 550000}
    
    context = {
        'course_info': course_info,
        'bim_subjects': bim_subjects,
        'fee_structure': fee_structure,
    }
    return render(request, 'campus/bim_course_details.html', context)

@login_required
@admin_required
def view_attendance(request, role=None):
    try:
        if role:
            attendees = User.objects.filter(role=role)
        else:
            attendees = User.objects.filter(role='student')
        attendance_records = Attendance.objects.filter(
            student__in=attendees, date__gte=date.today().replace(day=1)
        ).order_by('date')
    except Exception as e:
        messages.error(request, f"Error loading attendance: {str(e)}")
        attendance_records = []

@login_required
@student_required
def submit_assignment(request):
    try:
        profile = StudentProfile.objects.get(user=request.user)
        assignments = Assignment.objects.filter(semester=profile.semester, due_date__gte=date.today()).order_by('due_date')
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        assignments = []
    return render(request, 'campus/assignment_list.html', {'assignments': assignments})

@login_required
@student_required
def assignment_detail(request, pk):
    assignment = Assignment.objects.get(id=pk)
    submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
    
    if request.method == 'POST':
        if submission:
            messages.error(request, "You have already submitted this assignment.")
            return redirect('assignment_detail', pk=pk)

        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                submission = form.save(commit=False)
                submission.assignment = assignment
                submission.student = request.user
                submission.save()
                
                # Notify Teacher
                create_notification(
                    f"New Submission: {request.user.get_full_name()} submitted {assignment.title}",
                    request.user, 
                    recipient=assignment.teacher
                )
                
                messages.success(request, "Assignment submitted successfully!")
                return redirect('assignment_detail', pk=pk)
            except Exception as e:
                messages.error(request, f"Error submitting assignment: {e}")
    else:
        form = SubmissionForm()
    return render(request, 'campus/assignment_detail.html', {'assignment': assignment, 'form': form, 'submission': submission})

@login_required
@student_required
def view_exam_dates(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    exams = ExamRoutine.objects.filter(subject__semester=profile.semester, date__gte=date.today()).order_by('date')
    routine_images = ExamRoutine.objects.filter(semester=profile.semester, file__isnull=False).order_by('-id')
    return render(request, 'campus/view_exam_dates.html', {'exams': exams, 'routine_images': routine_images})

@login_required
@student_required
def view_events(request):
    events = Event.objects.filter(date__gte=date.today()).order_by('date')
    return render(request, 'campus/view_events.html', {'events': events})

@login_required
@student_required
def view_notifications(request):
    from .models import Notification
    from django.db.models import Q
    # Fetch all notifications for this user (Global + Targeted + Semester)
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    semester_filter = Q(recipient=None, semester=profile.semester) if profile.semester else Q(recipient=None, semester__isnull=True)
    
    notifications = Notification.objects.filter(
        Q(recipient=request.user) | (Q(recipient__isnull=True) & Q(semester__isnull=True)) | semester_filter
    ).order_by('-created_at')
    
    return render(request, 'campus/view_notifications.html', {'notifications': notifications})

@login_required
@student_required
def check_fee_status(request):
    fees = FeeDue.objects.filter(student=request.user).order_by('due_date')
    return render(request, 'campus/check_fee_status.html', {'fees': fees})

@login_required
@student_required
def view_my_attendance(request):
    attendance_records = Attendance.objects.filter(student=request.user).order_by('-date')
    return render(request, 'campus/view_attendance.html', {'attendance_records': attendance_records})

@login_required
@admin_required
def approve_user(request, user_id):
    from django.shortcuts import get_object_or_404
    user = get_object_or_404(User, id=user_id)
    user.is_approved = True
    user.save()
    
    # Optional: Send approval email
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        send_mail(
            'Account Approved',
            f'Hello {user.first_name},\n\nYour account has been approved by the admin. You can now login.',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=True,
        )
    except Exception:
        pass
        
    messages.success(request, f"User {user.email} has been approved.")
    return redirect('admin_dashboard')
