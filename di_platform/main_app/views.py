import ast
import csv
from datetime import datetime

from django.contrib.auth.decorators import user_passes_test
from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect
from courses_app.models import Collection
from django.urls import reverse

from profile_app.models import Program, Profile
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from .forms import AttendanceForm, Planning_form
from main_app.models import Attendance, Planning_prof

from profile_app.models import can_take_attendance
from django.db.models import Q

from django.db.models import Count


def index(request):
    if request.user.is_authenticated:
        return redirect('courses_app:collections')

    return redirect('profile_app:login')


def restricted(request):
    return render(request, 'restricted.html')

def calendar(request):
    is_admin = request.user.groups.filter(name='admin').exists()
    if is_admin:
        programs = Program.objects.all()
    else:
        programs = Program.objects.filter(id=request.user.profile.program.id)

    return render(request, 'calendar.html', {'programs': programs})

def leaderboards(request):
    if request.user.groups.filter(name__in=['admin', 'teacher']).exists():
        programs = Program.objects.all()
        return render(request, 'leaderboards.html', {'program_list': programs})
    
    return redirect('main_app:pk_leaderboard', program_id=request.user.profile.program.id)

def terms(request):
    return render(request, 'prospect_terms.html')

def privacy(request):
    return render(request, 'prospect_privacy.html')

def class_leaderboard(request, program_id=None):
    is_admin = request.user.groups.filter(name='admin').exists()
    is_teacher = request.user.groups.filter(name='teacher').exists()
    program_participants = {}

    if is_teacher and program_id==None:
        return redirect('main_app:index')
    elif is_teacher or is_admin:
        profiles = Program.objects.get(pk=program_id).profile_set
    else:
        profiles = request.user.profile.program.profile_set

    profiles = profiles.annotate(total_points=Coalesce(Sum(F('done_chapters__points_value')),0) + F('bonus_points') )
    profiles = profiles.order_by('-total_points')
    for idx, profile in enumerate(profiles, 1):
        if is_teacher:
            program_participants.update({idx : profile})
        elif idx < 5:
            program_participants.update({idx : profile})
        elif idx > 5 and request.user.profile not in program_participants.values():
            if profile == request.user.profile:
                program_participants.update({idx : profile})
                break
            else:
                continue
        elif idx == 5:
            if request.user.profile in program_participants.values():
                program_participants.update({idx : profile})
                break
            else:
                program_participants.update({idx : profile})
                continue
        else:
            program_participants.update({idx : profile})
            break

    program = Program.objects.get(id=program_id)
    return render(request, 'class_leaderboard.html', {'program_participants': program_participants, 'program': program})



# @user_passes_test(can_take_attendance, login_url='/welcome/')
# def attendance_filter(request):
#     if request.method == "POST":
#         program_id = request.POST.get('program_choice')
#         session = request.POST.get('gender')
#         program = Program.objects.get(pk=program_id)
#         student_list = [student for student in program.profile_set.all()]
#         return render(request, 'attendance.html', {"students": student_list, "program": program, "session": session})
#     else:
#         program_options = Program.objects.all()
#         return render(request, 'attendance_filter.html', {"program_options": program_options})



# def attendance(request, program_id):
#     list_program = Program.objects.all()
#     student_list = Profile.objects.filter(program_id=program_id)
#     program = Program.objects.get(id=program_id)
#     if request.method == "POST":
#         checked_students = request.POST.getlist('checked')
#         for student in student_list:
#             if str(student) in checked_students:
#                 Attendance(profile_id=student.id, program_id=program_id, session=session).save()
#             else:
#                 continue
#
#         # Here post new data to an excell spreadsheet or make spreadsheet auto update when db updates..
#         return redirect('main_app:index')
#     else:
#         return render(request, 'attendance_01.html', {"program": program,
#                                                       'list_program':list_program})


def take_attendance(request, program_id):
    list_program = Program.objects.all()
    student_list = Profile.objects.filter(program_id=program_id)
    program = Program.objects.get(id=program_id)
    count = student_list.count()
    attendance_formset = formset_factory(AttendanceForm, extra=count)

    # Those final status stuff
    # Getting two same date for one student and change the final status accordingly
    # py_student=Profile.objects.filter(program_id=1)
    # list_duplicate_att=[]
    # for student in py_student:
    #     att_py = Attendance.objects.filter(program_id=1, student=student)
    #     x= att_py.values('date').annotate(Count('id')).order_by('date').filter(id__count__gt=1)
    #     y=Attendance.objects.filter(date__in=[item['date'] for item in x])


    if request.method == "POST":
        formset = attendance_formset(request.POST)
        # list = zip(student_list, formset)
        hours = request.POST.get('teacher_hours')
        date1 = request.POST.get('date').split(" ")[0]
        date = datetime.strptime(date1, '%m/%d/%Y').strftime("%Y-%m-%d")
        session = request.POST.get('session')
        if not session:
            session="AM"
        teacher = request.user.profile

        if formset.is_valid():
            for form, student in zip(formset, student_list):
                print("JANE")
                status = form.cleaned_data.get('status', "Present")
                comments = form.cleaned_data.get('comments')

                try:
                    check_attendance = Attendance.objects.get(session=session, date=date,
                                                             student=student, program=program)
                except Attendance.DoesNotExist:
                    check_attendance = None
                #     If a same attendance exists, modify it
                if check_attendance:
                    if check_attendance.status!=status:
                        check_attendance.status = status
                    if check_attendance.comments != comments :
                        check_attendance.comments = comments
                    if check_attendance.teacher != teacher:
                        check_attendance.teacher = teacher
                    if check_attendance.teacher_hours != hours:
                        check_attendance.teacher_hours = hours
                    check_attendance.save()
                else:
                    new_attendance = Attendance(
                        teacher=teacher,
                        student=student,
                        program=program,
                        date=date,
                        session=session,
                        status=status,
                        comments=comments,
                        teacher_hours=hours
                        )
                    new_attendance.save()

        #             Trying to define the final attendance status for Python bootcamp
        #         att_am = Attendance.objects.filter(date=date, program=program, student=student, session="AM")
        #         att_pm = Attendance.objects.filter(date=date, program=program, student=student, session="PM")
        #         if att_am.status=="Present" and att_pm.status=="Present":
        #             att_am.status_hard = att_pm.status_hard = "Present"

        return redirect('main_app:index')
    else:
        list = zip(student_list, attendance_formset())
        return render(request, 'attendance_01.html', {'program': program,
                                                      'list_program': list_program,
                                                      'students': student_list,
                                                      'formset': attendance_formset(),
                                                      'list': list, })


def attendance_table(request, program_id):
    list_program = Program.objects.all()
    student_list = Profile.objects.filter(program_id=program_id)
    program = Program.objects.get(id=program_id)
    list1=[]
    for student in student_list:
        total_presence = Attendance.objects.filter(student=student, status="Present").count()
        total_absence = Attendance.objects.filter(student=student, status="Absent").count()
        total_late = Attendance.objects.filter(student=student, status="Late").count()
        student_l = [student, total_presence, total_absence, total_late]
        list1.append(student_l)
    return render(request, "attendance_table.html", {'program': program,
                                                      'list_program':list_program,
                                                      'students':student_list,
                                                     'att_list':list1,
                                                     })


def student_attendance(request, student_id, program_id):
    program = Program.objects.get(id=program_id)
    student= Profile.objects.get(id=student_id)
    student_att = Attendance.objects.filter(student=student_id, program=program_id).order_by('date')
    return render(request,'student_attendance.html', {'attendance':student_att,
                                                      'program':program,
                                                      'student':student,
                              })


def planning_teacher(request, program_id):
    list_program = Program.objects.all()
    program = Program.objects.get(id=program_id)
    if request.method == "POST":
        apply_all = request.POST.get('for_all')
        form = Planning_form(request.POST)
        if form.is_valid():
            # Check if the modifications have to be applied on every week
            if apply_all:
                session=form.cleaned_data["session"]
                # Check with the session attribute in Python bootcamp case
                if program_id == 1:
                    try:
                        check_plan = Planning_prof.objects.filter(program=program, session=session)
                    except Planning_prof.DoesNotExist:
                        check_plan = None
                    check_plan.delete()
                else:
                    try:
                        check_plan = Planning_prof.objects.filter(program=program)
                    except Planning_prof.DoesNotExist:
                        check_plan = None
                    check_plan.delete()

                # Filtering: 12 weeks for Python and Js Full time
                if program_id == 1 or program_id == 2:
                    for i in range(1,13):
                        new_plan= Planning_prof(
                            prof=form.cleaned_data["prof"],
                            program=program,
                            week_num=i,
                            teacher_hours=form.cleaned_data["teacher_hours"],
                            session=session,
                            )
                        new_plan.save()
                else:
                    for i in range(1,17):
                        new_plan= Planning_prof(
                            prof=form.cleaned_data["prof"],
                            program=program,
                            week_num=i,
                            teacher_hours=form.cleaned_data["teacher_hours"],
                            session=form.cleaned_data["session"],
                            )
                        new_plan.save()
            # Create or modify the planning of a week
            else:
                week=form.cleaned_data["week_num"]
                day=form.cleaned_data["day"]
                session=form.cleaned_data["session"]
                # check_plan, created = Planning_prof.objects.get_or_create(week_num=week,program=program)
                # Check with the session attribute in Python bootcamp case
                if program_id == 1:
                    try:
                        check_plan = Planning_prof.objects.filter(program=program, session=session)
                    except Planning_prof.DoesNotExist:
                        check_plan = None
                else:
                    try:
                        check_plan = Planning_prof.objects.get(week_num=week,program=program, day=day)
                    except Planning_prof.DoesNotExist:
                        check_plan = None
                if check_plan:
                    check_plan.prof = form.cleaned_data["prof"]
                    check_plan.teacher_hours = form.cleaned_data["teacher_hours"]
                    check_plan.save()
                else:
                    new_plann= Planning_prof(
                        prof=form.cleaned_data["prof"],
                        program=program,
                        day=day,
                        week_num=week,
                        teacher_hours=form.cleaned_data["teacher_hours"],
                        session=session,
                        )
                    new_plann.save()
        return redirect('main_app:planning_teacher', program_id)
    else:
        form = Planning_form()
        py_bootcamp=Program.objects.get(id=1)
        planning_py_am = Planning_prof.objects.filter(program=py_bootcamp,session='AM').order_by("week_num")
        planning_py_pm = Planning_prof.objects.filter(program_id=1, session="PM").order_by("week_num")
        planning_list = Planning_prof.objects.filter(program_id=program_id).order_by("week_num")
    return render(request, "planning_teacher.html", {'program': program,
                                                     'list_program': list_program,
                                                     'form':form,
                                                     'list':planning_list,
                                                     "list_am":planning_py_am,
                                                     "list_pm":planning_py_pm,})


def export_to_csv(request, program_id):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report_attendance-{}.csv"'.format(datetime.today().date())
    writer = csv.writer(response)
    writer.writerow(
        ['Student', 'Total Days', 'Total Present', 'Total Absent', 'Total Late', 'Course'])

    # Data For Report
    program = Program.objects.get(id=program_id)
    attendance = Attendance.objects.filter(program=program)
    student_list = Profile.objects.filter(program_id=program_id)

    # Data Writing
    for student in student_list:
        row = []
        student_presence = attendance.filter(status="Present", student=student).count()
        student_absence = attendance.filter(status="Absent", student=student).count()
        student_late = attendance.filter(status="Late", student=student).count()
        row.append(student)
        row.append(60)
        row.append(student_presence)
        row.append(student_absence)
        row.append(student_late)
        row.append(program.name)
        writer.writerow(row)
    return response

def  export_csv_student(request, program_id, student_id):
    student=Profile.objects.get(id=student_id)
    program = Program.objects.get(id=program_id)
    attendance=Attendance.objects.filter(program=program, student=student).order_by('date')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance-{}-{}.csv"'.format(program, student)
    writer = csv.writer(response)
    writer.writerow(
        ['Day', 'Status', 'Session']
        )

    for day in attendance:
        row=[]
        row.append(day.date)
        row.append(day.status)
        row.append(day.session)
        writer.writerow(row)
    return response
