from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey('users.User', on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}),
    is_active = models.BooleanField(default=True)



class Enrollment(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_date = models.DateField(auto_now_add=True)
