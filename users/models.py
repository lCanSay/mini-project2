from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLES = (
        ('student', 'student'),
        ('teacher', 'teacher'),
        ('admin', 'admin'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='student')

    def __str__(self):
        return f"{self.username} ({self.role})"


