from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_welcome_email(student_email):
    send_mail(
        'Welcome!',
        'Thank you for registering as a student.',
        'admin@school.com',
        [student_email],
        fail_silently=False,
    )
