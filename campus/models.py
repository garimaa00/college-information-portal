
from django.conf import settings
from django.db import models
from users.models import CustomUser


class Faculty(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    semester = models.IntegerField()

    def __str__(self):
        return f"{self.name} (Sem {self.semester})"

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    semester = models.IntegerField(default=1)
    section = models.CharField(max_length=10, blank=True, null=True)
    attended_days = models.IntegerField(default=0)
    total_days = models.IntegerField(default=0)  # For attendance percentage

class TeacherProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject)

# class Attendance(models.Model):
#     student = models.ForeignKey(CustomUser, related_name='student_attendance', on_delete=models.CASCADE)
#     date = models.DateField(auto_now_add=True)
#     present = models.BooleanField(default=True)
#     teacher = models.ForeignKey(CustomUser, related_name='marked_by', on_delete=models.SET_NULL, null=True)
class Attendance(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='student_attendance', limit_choices_to={'role': 'student'}, on_delete=models.CASCADE)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='teacher_attendance', limit_choices_to={'role': 'teacher'}, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    present = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.student.email} - {self.date} ({'Present' if self.present else 'Absent'})"
    
class TeacherAttendance(models.Model):
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='campus_teacher_records'
    )
    date = models.DateField(auto_now_add=True)
    present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.teacher.email} - {self.date}"
    
class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    due_date = models.DateField()
    semester = models.IntegerField()
    file = models.FileField(upload_to='assignments/', blank=True, null=True)

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)

class ExamRoutine(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    details = models.TextField(blank=True)
    file = models.FileField(upload_to='exam_routines/', blank=True, null=True)
    semester = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=200, blank=True, help_text="Optional title for the routine image")
    start_date = models.DateField(null=True, blank=True, help_text="Exam starting date")
    end_date = models.DateField(null=True, blank=True, help_text="Exam ending date")

class FeeDue(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    type = models.CharField(max_length=50)  # e.g., tournament

    def __str__(self):
        return self.title

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

class Testimonial(models.Model):  # Optional bonus
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    
class CollegeInfo(models.Model):
    about_bim = models.TextField(default="ShankerDev Campus offers a Bachelor in Information Management (BIM) program.")
    location = models.CharField(max_length=100, default="Kathmandu, Nepal")

class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_notifications')
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    semester = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.message[:50]}... ({self.created_at.date()})"



class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, default="No description available")
    duration = models.CharField(max_length=50, default="No Duration matched")
    location = models.CharField(max_length=200, default="Unknown location")
    available_seats = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    

class UserNotificationTracker(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=[('attendance', 'Attendance'), ('assignment', 'Assignment'), ('fee_reminder', 'Fee Reminder')])
    last_sent_date = models.DateField()

    class Meta:
        unique_together = ('user', 'notification_type')
    

