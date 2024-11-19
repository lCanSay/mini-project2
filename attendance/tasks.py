from celery import shared_task
from logger.logging import logger
from django.core.mail import send_mail

@shared_task
def notify_student_about_absence(student_email, course_name):
    try:
        logger.info(f"Sending absence notification to {student_email}")
        send_mail(
            'Attendance Alert',
            f'Marked absent in {course_name}.',
            [student_email],
            fail_silently=False,
        )
        logger.info(f"Absence notification sent to {student_email}")
    except Exception as e:
        logger.error(f"Error sending absence notification to {student_email}: {e}")