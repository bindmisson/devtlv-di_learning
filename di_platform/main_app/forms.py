from django import forms
from .models import *


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['status', 'comments']

    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        self.fields['comments'].required = False


class Planning_form(forms.ModelForm):
    class Meta:
        model=Planning_prof
        fields = ['prof','program', 'week_num', 'day', 'teacher_hours', 'session']

    def __init__(self, *args, **kwargs):
        super(Planning_form, self).__init__(*args, **kwargs)
        self.fields['session'].required = False
        self.fields['day'].required = False
        self.fields['week_num'].required = False