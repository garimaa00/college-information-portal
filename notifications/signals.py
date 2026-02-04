from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from attendance.models import StudentAttendance

@receiver(post_save, sender=StudentAttendance)
def send_notification(sender, instance, **kwargs):
    if instance.percentage < 80:
        # Email
        send_mail(
            'Low Attendance Alert',
            f'Your attendance is {instance.percentage}%.',
            'admin@shankerdev.com',
            [instance.student.email],
        )
        # SMS (optional, requires Twilio setup)
        # from twilio.rest import Client
        # client = Client('TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN')
        # client.messages.create(to=instance.student.phone, from_='your_twilio_number', body='Low attendance alert.')