
# from django.contrib.auth.views import LoginView
# from django.shortcuts import render, redirect
# from django.contrib.auth import login
# from users.forms import CustomUserCreationForm, CustomAuthenticationForm
# from users.models import CustomUser
# from events.models import Event
# from django.utils import timezone
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# def home_view(request):
#     return render(request, 'home.html')  # Create a home.html template

# class CustomLoginView(LoginView):
#     template_name = 'registration/login.html'
#     form_class = CustomAuthenticationForm

#     def form_valid(self, form):
#         response = super().form_valid(form)
#         if self.request.user.role == 'student':
#             return redirect('student_dashboard')
#         elif self.request.user.role == 'teacher':
#             return redirect('teacher_dashboard')
#         elif self.request.user.role == 'admin':
#             return redirect('admin_dashboard')
#         return response

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         bim_subjects = {
#             1: ["Principles of Management", "English Composition", "Basic Mathematics", "Computer Information System", "Digital Logic Design"],
#             2: ["Business Communications", "Digital Logic", "Discrete Structure", "Object Oriented Programming with Java", "Organizational Behavior & Human Resource Management"],
#             3: ["Business Statistics", "Data Structure and Algorithms", "Financial Accounting", "Microprocessor and Computer Architecture", "Web Technology I"],
#             4: ["Business Data Communication and Networking", "Cost and Management Accounting", "Database Management System", "Economics for Business", "Operating System", "Web Technology II"],
#             5: ["Artificial Intelligence", "Fundamentals of Marketing", "Information Security", "Programming with Python", "Software Design and Development"],
#             6: ["Business Environment", "Business Information Systems", "Business Research Methods", "Fundamentals of Corporate Finance", "IT Ethics and Cybersecurity", "Project"],
#             7: ["E-Commerce and Internet Marketing", "Elective I", "Operations Management", "Sociology for Business Management", "Strategic Management"],
#             8: ["Business Intelligence", "Digital Economy", "Economics of Information and Communication", "Elective II", "Internship"],
#         }
#         fee_structure = {2079: 475000, 2080: 500000, 2081: 525000, 2082: 550000}
#         events = Event.objects.filter(date__gte=timezone.now()).order_by('date')[:3]
#         context.update({'bim_subjects': bim_subjects, 'fee_structure': fee_structure, 'events': events})
#         return context

# @login_required
# def student_dashboard(request):
#     return render(request, 'student_dashboard.html', {'user': request.user})

# @login_required
# def teacher_dashboard(request):
#     return render(request, 'teacher_dashboard.html', {'user': request.user})

# @login_required
# def admin_dashboard(request):
#     return render(request, 'admin_dashboard.html', {'user': request.user})

# def register_view(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('login')
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'registration/register.html', {'form': form})

# def bim_course_details(request):
#     bim_subjects = {
#         1: ["Principles of Management", "English Composition", "Basic Mathematics", "Computer Information System", "Digital Logic Design"],
#         2: ["Business Communications", "Digital Logic", "Discrete Structure", "Object Oriented Programming with Java", "Organizational Behavior & Human Resource Management"],
#         3: ["Business Statistics", "Data Structure and Algorithms", "Financial Accounting", "Microprocessor and Computer Architecture", "Web Technology I"],
#         4: ["Business Data Communication and Networking", "Cost and Management Accounting", "Database Management System", "Economics for Business", "Operating System", "Web Technology II"],
#         5: ["Artificial Intelligence", "Fundamentals of Marketing", "Information Security", "Programming with Python", "Software Design and Development"],
#         6: ["Business Environment", "Business Information Systems", "Business Research Methods", "Fundamentals of Corporate Finance", "IT Ethics and Cybersecurity", "Project"],
#         7: ["E-Commerce and Internet Marketing", "Elective I", "Operations Management", "Sociology for Business Management", "Strategic Management"],
#         8: ["Business Intelligence", "Digital Economy", "Economics of Information and Communication", "Elective II", "Internship"],
#     }
#     fee_structure = {2079: 475000, 2080: 500000, 2081: 525000, 2082: 550000}
#     return render(request, 'bim_course_details.html', {'bim_subjects': bim_subjects, 'fee_structure': fee_structure})

from asyncio import Task
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from campus.forms import ExamRoutineForm
from campus.models import Course, ExamRoutine
from notifications.models import Notification
from users.forms import CustomUserCreationForm, CustomAuthenticationForm
from users.models import CustomUser
from events.models import Event
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

def home_view(request):
    from campus.models import Event, StudentProfile, Course
    from django.db.models import Count
    from django.utils import timezone

    # Fetch Events
    events = Event.objects.filter(date__gte=timezone.now().date()).order_by('date')[:3]
    
    # Fetch Courses (for Seats and Info)
    courses = Course.objects.all().order_by('name')
    
    # Student Stats
    semester_counts = StudentProfile.objects.values('semester').annotate(count=Count('user')).order_by('semester')
    
    # Fee Structure (Hardcoded for display)
    fee_structure = {
        '2079': '4,75,000',
        '2080': '5,00,000',
        '2081': '5,25,000',
        '2082': '5,50,000'
    }

    bim_subjects = {
        1: ["Principles of Management", "English Composition", "Basic Mathematics", "Computer Information System", "C Programming"],
        2: ["Business Communications", "Digital Logic", "Discrete Structure", "Object Oriented Programming with Java", "Organizational Behavior & Human Resource Management"],
        3: ["Business Statistics", "Data Structure and Algorithms", "Financial Accounting", "Microprocessor and Computer Architecture", "Web Technology I"],
        4: ["Business Data Communication and Networking", "Cost and Management Accounting", "Database Management System", "Economics for Business", "Operating System", "Web Technology II"],
        5: ["Artificial Intelligence", "Fundamentals of Marketing", "Information Security", "Programming with Python", "Software Design and Development"],
        6: ["Business Environment", "Business Information Systems", "Business Research Methods", "Fundamentals of Corporate Finance", "IT Ethics and Cybersecurity", "Project"],
        7: ["E-Commerce and Internet Marketing", "Elective I", "Operations Management", "Sociology for Business Management", "Strategic Management"],
        8: ["Business Intelligence", "Digital Economy", "Economics of Information and Communication", "Elective II", "Internship"],
    }

    context = {
        'events': events,
        'courses': courses,
        'semester_counts': semester_counts,
        'fee_structure': fee_structure,
        'bim_subjects': bim_subjects,
    }
    return render(request, 'home.html', context)

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = CustomAuthenticationForm

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        if user.role == 'student':
            return redirect('student_dashboard')
        elif user.role == 'teacher':
            return redirect('teacher_dashboard')
        elif user.role == 'admin':
            return redirect('admin_dashboard')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bim_subjects = {
            1: ["Principles of Management", "English Composition", "Basic Mathematics", "Computer Information System", "C Programming"],
            2: ["Business Communications", "Digital Logic", "Discrete Structure", "Object Oriented Programming with Java", "Organizational Behavior & Human Resource Management"],
            3: ["Business Statistics", "Data Structure and Algorithms", "Financial Accounting", "Microprocessor and Computer Architecture", "Web Technology I"],
            4: ["Business Data Communication and Networking", "Cost and Management Accounting", "Database Management System", "Economics for Business", "Operating System", "Web Technology II"],
            5: ["Artificial Intelligence", "Fundamentals of Marketing", "Information Security", "Programming with Python", "Software Design and Development"],
            6: ["Business Environment", "Business Information Systems", "Business Research Methods", "Fundamentals of Corporate Finance", "IT Ethics and Cybersecurity", "Project"],
            7: ["E-Commerce and Internet Marketing", "Elective I", "Operations Management", "Sociology for Business Management", "Strategic Management"],
            8: ["Business Intelligence", "Digital Economy", "Economics of Information and Communication", "Elective II", "Internship"],
        }
        fee_structure = {2079: 475000, 2080: 500000, 2081: 525000, 2082: 550000}
        events = Event.objects.filter(date__gte=timezone.now()).order_by('date')[:3]
        context.update({'bim_subjects': bim_subjects, 'fee_structure': fee_structure, 'events': events})
        return context

@login_required
def student_dashboard(request):
    return render(request, 'student_dashboard.html', {'user': request.user})

@login_required
def teacher_dashboard(request):
    if request.user.role != 'teacher':
        return redirect('login')
    if request.method == 'POST' and 'own_attendance' in request.POST:
        CustomUser.objects.update_or_create(
            id=request.user.id,
            defaults={'attendance': {'date': timezone.now().date(), 'present': request.POST.get('present') == 'on'}}
        )
    if request.method == 'POST' and 'student_attendance' in request.POST:
        student_id = request.POST.get('student_id')
        student = CustomUser.objects.get(id=student_id)
        CustomUser.objects.update_or_create(
            id=student.id,
            defaults={'attendance': {'date': timezone.now().date(), 'present': request.POST.get('student_present') == 'on'}}
        )
    if request.method == 'POST' and 'assign_task' in request.POST:
        student_id = request.POST.get('student_id')
        student = CustomUser.objects.get(id=student_id)
        Task.objects.create(
            teacher=request.user,
            student=student,
            title=request.POST.get('task_title'),
            description=request.POST.get('task_description'),
            due_date=request.POST.get('due_date')
        )
    attendances = getattr(request.user, 'attendance', [])  # Assuming attendance is a related field or list
    students = CustomUser.objects.filter(role='student')
    tasks = Task.objects.filter(teacher=request.user)
    return render(request, 'teacher_dashboard.html', {
        'user': request.user,
        'attendances': attendances,
        'students': students,
        'tasks': tasks
    })

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('login')
    if request.method == 'POST' and 'create_course' in request.POST:
        Course.objects.create(name=request.POST.get('course_name'), available_seats=request.POST.get('seats'))
    if request.method == 'POST' and 'set_exam' in request.POST:
        course_id = request.POST.get('course_id')
        course = Course.objects.get(id=course_id)
        ExamRoutineForm.objects.create(course=course, date=request.POST.get('exam_date'), routine=request.POST.get('routine'))
    if request.method == 'POST' and 'post_event' in request.POST:
        Event.objects.create(title=request.POST.get('event_title'), description=request.POST.get('event_description'), date=request.POST.get('event_date'))
    if request.method == 'POST' and 'send_notification' in request.POST:
        user_id = request.POST.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        Notification.objects.create(user=user, message=request.POST.get('notification_message'))
    if request.method == 'POST' and 'update_seats' in request.POST:
        course_id = request.POST.get('course_id')
        course = Course.objects.get(id=course_id)
        course.available_seats = request.POST.get('new_seats')
        course.save()
    courses = Course.objects.all()
    exams = ExamRoutine.objects.all()
    events = Event.objects.all()
    users = CustomUser.objects.all()
    notifications = Notification.objects.all()
    return render(request, 'admin_dashboard.html', {
        'user': request.user,
        'courses': courses,
        'exams': exams,
        'events': events,
        'users': users,
        'notifications': notifications
    })

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'teacher':
                return redirect('teacher_dashboard')
            elif user.role == 'admin':
                return redirect('admin_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def bim_course_details(request):
    bim_subjects = {
        1: ["Principles of Management", "English Composition", "Basic Mathematics", "Computer Information System", "Digital Logic Design"],
        2: ["Business Communications", "Digital Logic", "Discrete Structure", "Object Oriented Programming with Java", "Organizational Behavior & Human Resource Management"],
        3: ["Business Statistics", "Data Structure and Algorithms", "Financial Accounting", "Microprocessor and Computer Architecture", "Web Technology I"],
        4: ["Business Data Communication and Networking", "Cost and Management Accounting", "Database Management System", "Economics for Business", "Operating System", "Web Technology II"],
        5: ["Artificial Intelligence", "Fundamentals of Marketing", "Information Security", "Programming with Python", "Software Design and Development"],
        6: ["Business Environment", "Business Information Systems", "Business Research Methods", "Fundamentals of Corporate Finance", "IT Ethics and Cybersecurity", "Project"],
        7: ["E-Commerce and Internet Marketing", "Elective I", "Operations Management", "Sociology for Business Management", "Strategic Management"],
        8: ["Business Intelligence", "Digital Economy", "Economics of Information and Communication", "Elective II", "Internship"],
    }
    fee_structure = {2079: 475000, 2080: 500000, 2081: 525000, 2082: 550000}
    return render(request, 'bim_course_details.html', {'bim_subjects': bim_subjects, 'fee_structure': fee_structure})

def logout_view(request):
    logout(request)
    return redirect('login')
