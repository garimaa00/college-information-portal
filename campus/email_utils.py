"""
Email utilities for ShankerDev Campus Portal
Functions to send various types of emails with HTML templates
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_welcome_email(user):
    """Send welcome email to newly registered users"""
    try:
        context = {
            'user_name': f"{user.first_name} {user.last_name}" if user.first_name else user.email,
            'email': user.email,
            'role': user.role,
            'date': user.date_joined.strftime('%B %d, %Y'),
            'subject': 'Welcome to ShankerDev Campus Portal'
        }
        
        html_content = render_to_string('emails/welcome_email.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject='Welcome to ShankerDev Campus Portal',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Welcome email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False


def send_attendance_alert_email(student, attendance_percentage):
    """Send low attendance alert to students"""
    try:
        context = {
            'student_name': f"{student.first_name} {student.last_name}" if student.first_name else student.email,
            'attendance_percentage': f"{attendance_percentage:.1f}",
            'subject': 'Low Attendance Alert - Action Required'
        }
        
        html_content = render_to_string('emails/attendance_alert_email.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject='Low Attendance Alert - ShankerDev Campus',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[student.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Attendance alert sent to {student.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send attendance alert to {student.email}: {str(e)}")
        return False


def send_assignment_notification_email(student, assignment, teacher):
    """Send new assignment notification to students"""
    try:
        context = {
            'student_name': f"{student.first_name} {student.last_name}" if student.first_name else student.email,
            'assignment_title': assignment.title,
            'subject': assignment.subject.name,
            'semester': assignment.semester,
            'due_date': assignment.due_date.strftime('%B %d, %Y'),
            'description': assignment.description,
            'teacher_name': f"{teacher.first_name} {teacher.last_name}" if teacher.first_name else teacher.email,
            'subject': f'New Assignment: {assignment.title}'
        }
        
        html_content = render_to_string('emails/assignment_notification_email.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=f'New Assignment: {assignment.title}',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[student.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Assignment notification sent to {student.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send assignment notification to {student.email}: {str(e)}")
        return False


def send_fee_reminder_email(student, amount, due_date):
    """Send fee payment reminder to students"""
    try:
        context = {
            'student_name': f"{student.first_name} {student.last_name}" if student.first_name else student.email,
            'amount': f"{amount:,.2f}",
            'due_date': due_date.strftime('%B %d, %Y'),
            'subject': 'Fee Payment Reminder'
        }
        
        html_content = render_to_string('emails/fee_reminder_email.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject='Fee Payment Reminder - ShankerDev Campus',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[student.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Fee reminder sent to {student.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send fee reminder to {student.email}: {str(e)}")
        return False


def send_bulk_email(recipient_list, subject, html_template, context):
    """Send bulk emails to multiple recipients"""
    success_count = 0
    failed_count = 0
    
    for recipient in recipient_list:
        try:
            html_content = render_to_string(html_template, context)
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient]
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            
            success_count += 1
            logger.info(f"Bulk email sent to {recipient}")
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to send bulk email to {recipient}: {str(e)}")
    
    return success_count, failed_count
