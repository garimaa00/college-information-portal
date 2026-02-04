from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import StudentAttendance

@receiver(post_save, sender=StudentAttendance)
def update_attendance_percentage(sender, instance, **kwargs):
    total_days = StudentAttendance.objects.filter(student=instance.student, course=instance.course).count()
    present_days = StudentAttendance.objects.filter(student=instance.student, course=instance.course, present=True).count()
    if total_days > 0:
        instance.percentage = (present_days / total_days) * 100
        instance.save()

    if instance.percentage < 80:
        send_mail(
            'Low Attendance Alert',
            f'Your attendance for {instance.course.name} is {instance.percentage:.1f}%.',
            'from@example.com',  # Replace with your email or configure in settings.py
            [instance.student.email],
            fail_silently=True,
        )