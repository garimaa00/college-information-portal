from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import StudentAttendance, TeacherAttendance  # Updated import
from django.contrib.auth import get_user_model
from datetime import date
from django.core.paginator import Paginator

User = get_user_model()

def teacher_required(function):
    return user_passes_test(lambda u: u.role == 'teacher' and u.is_authenticated)(function)

def admin_or_teacher_required(function):
    return user_passes_test(lambda u: (u.role in ['admin', 'teacher'] and u.is_authenticated))(function)

@login_required
@teacher_required
def mark_attendance(request):
    if request.method == 'POST':
        students = request.POST.getlist('students')
        course_id = request.POST.get('course_id')  # Assuming course_id is sent via form
        if not course_id:
            messages.error(request, 'Course ID is required.')
            return redirect('attendance:mark_attendance')
        for student_id in students:
            student = User.objects.get(id=student_id)
            present = student_id in request.POST.getlist('present_students', [])
            StudentAttendance.objects.update_or_create(
                student=student,
                course_id=course_id,
                date=date.today(),
                defaults={'present': present}
            )
        messages.success(request, 'Attendance marked successfully.')
        return redirect('attendance:view_attendance', role='student')  # Updated redirect
    students = User.objects.filter(role='student')
    return render(request, 'attendance/mark_attendance.html', {'students': students})

@login_required
@teacher_required
def mark_teacher_attendance(request):
    if request.method == 'POST':
        present = request.POST.get('present') == 'on'
        TeacherAttendance.objects.update_or_create(
            teacher=request.user,
            date=date.today(),
            defaults={'present': present}
        )
        messages.success(request, 'Teacher attendance marked.')
        return redirect('attendance:view_attendance', role='teacher')  # Updated redirect
    return render(request, 'attendance/mark_teacher_attendance.html')

@login_required
def view_attendance(request, role=None):
    if role == 'teacher':
        attendance_records = TeacherAttendance.objects.filter(
            teacher=request.user,
            date__gte=date.today().replace(day=1)
        ).order_by('date')
    else:  # Default to student role or all students
        attendees = User.objects.filter(role='student') if not role else User.objects.filter(role=role)
        attendance_records = StudentAttendance.objects.filter(
            student__in=attendees,
            date__gte=date.today().replace(day=1)
        ).order_by('date')
    return render(request, 'attendance/view_attendance.html', {
        'attendance_records': attendance_records,
        'role': role or 'student'
    })

@login_required
@admin_or_teacher_required
def attendance_list(request):
    # Combine student and teacher attendance
    student_attendance = StudentAttendance.objects.all().order_by('date')
    teacher_attendance = TeacherAttendance.objects.all().order_by('date')
    
    # Paginate the combined records (e.g., 10 per page)
    all_attendance = list(student_attendance) + list(teacher_attendance)
    all_attendance.sort(key=lambda x: x.date, reverse=True)  # Sort by date descending
    paginator = Paginator(all_attendance, 10)  # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'attendance/attendance_list.html', {
        'page_obj': page_obj,
        'role': 'all'  # Indicate all roles
    })