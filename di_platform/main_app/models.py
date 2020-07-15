from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils import timezone

from profile_app.models import Profile, Program


class Attendance(models.Model):
    session_choices = (
        ('am', 'AM'),
        ('pm', 'PM'),
        )
    class_attendance = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        )
    hours = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        )
    teacher = models.ForeignKey(Profile, on_delete=models.DO_NOTHING, related_name="teacher", default=1)
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="student", default=1)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    date =models.DateField( default=None)
    session = models.CharField(max_length=3, choices=session_choices, null=True)
    status = models.CharField(max_length=50, choices=class_attendance, default="Present")

    status_hard = models.CharField(max_length=50, choices=class_attendance, default="Present", null=True)
    status_soft = models.CharField(max_length=50, choices=class_attendance, default="Present", null=True)

    comments = models.CharField(max_length=300, default=None, null=True)
    teacher_hours = models.IntegerField(choices=hours, default=None, null=True)

    def __str__(self):
        return str(self.date)



class Planning_prof(models.Model):
    DAYS= (
        ("SUNDAY", "SUNDAY"),
        ("MONDAY", "MONDAY"),
        ("TUESDAY", "TUESDAY"),
        ("WEDNESDAY", "WEDNESDAY"),
        ("THURSDAY","THURSDAY")
    )
    hours = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        )
    session_choices = (
        ('AM', 'AM'),
        ('PM', 'PM'),
        )
    prof = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="professor", limit_choices_to={'groups__name': "teacher"})
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    week_num =  models.IntegerField(null=True)
    day = models.CharField(max_length=50, choices=DAYS, default="All", null=True)
    teacher_hours = models.IntegerField(choices=hours, null=True)
    session = models.CharField(max_length=3, choices=session_choices, null=True)
