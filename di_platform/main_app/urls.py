from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'main_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('restricted/', views.restricted, name='restricted'),
    path('leaderboard/<int:program_id>/', views.class_leaderboard, name='pk_leaderboard'),
    path('leaderboards/', views.leaderboards, name='leaderboards'),
    path('calendar/', views.calendar, name='calendar'),
    path('student_attendance/<int:student_id>/<int:program_id>', views.student_attendance, name='student_attendance'),
    path('attendance_table/<int:program_id>', views.attendance_table, name='attendance_table'),
    path('export_to_csv/<int:program_id>', views.export_to_csv, name='export_to_csv'),
    path('export_csv_student/<int:program_id>/<int:student_id>', views.export_csv_student, name='export_csv_student'),
    path('planning_teacher/<int:program_id>', views.planning_teacher, name='planning_teacher'),
    path('take_attendance/<int:program_id>', views.take_attendance, name='take_attendance'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
]

