from django.db import models
from users.models import CustomUser
from courses.models import Course

class StudentAttendance(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    present = models.BooleanField(default=False)
    percentage = models.FloatField(default=0.0)  # Calculated field (update via signal)

    def __str__(self):
        return f"{self.student.email} - {self.course.name} - {self.date}"

class TeacherAttendance(models.Model):
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='attendance_teacher_records'  # Unique related_name
    )
    date = models.DateField(auto_now_add=True)
    present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.teacher.email} - {self.date}"