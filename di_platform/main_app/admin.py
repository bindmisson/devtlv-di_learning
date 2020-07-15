from django.db import models
from martor.widgets import AdminMartorWidget
from django.contrib import admin
from main_app.models import Attendance, Planning_prof
from profile_app.models import Profile


class PageAttendance(admin.ModelAdmin):
    model = Attendance
    list_display = ('id', 'date', 'session', 'teacher', 'program', 'student', 'status', 'comments')
    # def get_profile_name(self, obj):
    #     return obj.student
    # def get_program_name(self, obj):
    #     return obj.program


class Planning(admin.ModelAdmin):
    model = Planning_prof
    list_display = ('id', 'prof', 'program', 'teacher_hours', 'week_num', 'session', 'day')


admin.site.register(Attendance, PageAttendance)
admin.site.register(Planning_prof, Planning)

