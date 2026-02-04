from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Attendance, StudentProfile, UserNotificationTracker
from .email_utils import send_attendance_alert_email, send_welcome_email
from django.conf import settings
from datetime import date


@receiver(post_save, sender=Attendance)
def update_attendance(sender, instance, created, **kwargs):
    if created:
        student = instance.student
        profile, _ = StudentProfile.objects.get_or_create(user=student)
        profile.attended_days += 1 if instance.present else 0
        profile.save()
        if profile.total_days > 0:
            attendance_percentage = (profile.attended_days / profile.total_days * 100)
            if attendance_percentage < 80:
                today = date.today()
                # Check if a notification has been sent today
                if not UserNotificationTracker.objects.filter(user=student, notification_type='attendance', last_sent_date=today).exists():
                    try:
                        send_attendance_alert_email(student, attendance_percentage)
                        # Update the tracker
                        UserNotificationTracker.objects.update_or_create(
                            user=student,
                            notification_type='attendance',
                            defaults={'last_sent_date': today}
                        )
                    except Exception:
                        pass


from django.contrib.auth import get_user_model
User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Send welcome email
        try:
            send_welcome_email(instance)
        except Exception:
            pass
            
        if instance.role == 'student':
            StudentProfile.objects.get_or_create(user=instance)
        elif instance.role == 'teacher':
            from .models import TeacherProfile
            TeacherProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'student':
        if hasattr(instance, 'studentprofile'):
             instance.studentprofile.save()
    elif instance.role == 'teacher':
        if hasattr(instance, 'teacherprofile'):
             instance.teacherprofile.save()