from django.shortcuts import render, redirect
from courses_app.models import *

from django.contrib.auth.decorators import login_required, user_passes_test
from profile_app.models import user_can_access_collection, get_user_collections, Program_Done_Chapters, Profile
from django.http import JsonResponse
from django.db.models import F, Sum
from di_platform.settings import LOGIN_URL
import json
from math import ceil

def calculate_section_progress(user, section):
    # All chapters in the section excluding group COurses and TEachers.
    section_total_points = section.chapters.all().exclude(group__in=["CO", "TE"]).aggregate(Sum('points_value'))
    # Which of the above has the user completed?
    section_chapters_completed = section.chapters.all().exclude(group__in=["CO", "TE"]) & user.profile.done_chapters.filter(program_done_chapters__program=user.profile.program)
    # Add the points of completed
    section_done_points = section_chapters_completed.aggregate(Sum('points_value')) 

    section_total_points = section_total_points["points_value__sum"] or -1 # In case of "None"
    section_done_points = section_done_points["points_value__sum"] or 0 # In case of "None"
    
    return (section_done_points, section_total_points)

def calculate_points_by_type(user):
    # Create dictionary of chapter groups with values 0
    total_points_by_group = {}
    for tup in Chapter.GROUP_CHOICES:
        total_points_by_group[tup[0]] = 0

    # Loop through all done chapters
    collection = user.profile.program.collection
    courses = collection.courses.all()
    for course in courses:
        sections = course.sections.all()
        for section in sections:
            section_chapters_completed = section.chapters.all() & user.profile.done_chapters.filter(program_done_chapters__program=user.profile.program)
            for chapter in section_chapters_completed:
                # Increment the points by the chapters points value per group
                total_points_by_group[chapter.group] += chapter.points_value or 0

    return total_points_by_group

def calculate_awarded_trophies(user):
    total_points_by_group = calculate_points_by_type(user)

    # pull trophy requirements from DB
    trophy_requirements = TrophyRequirements.objects.all().order_by('sort_order')
    user_trophies = []

    for trophy in trophy_requirements:
        has_requirements = True
        # compare trophy requirements to total_points_by_group.
        for tup in Chapter.GROUP_CHOICES:
            group = tup[0]
            if total_points_by_group[group] < getattr(trophy, group):
                has_requirements = False
                break
        if has_requirements:
            user_trophies.append(trophy)

    return user_trophies
    
    # profiles should also keep track of acknowledged trophys... (this info also passed to template in some form.)

    # when template is diplayed, if a trophy has not been acknowledged, then pop up "Congratulations"
    

   



@login_required(login_url=LOGIN_URL)
def section(request, collection_id, course_id, section_id, chapter_id=None):
    collection = Collection.objects.get(id=collection_id)
    course = Course.objects.get(id=course_id)
    section = Section.objects.get(id=section_id)
    chapter = None if chapter_id is None else Chapter.objects.get(id=chapter_id)
    done_chapters = list(Program_Done_Chapters.objects.filter(profile=request.user.profile, program=request.user.profile.program).values_list('chapter', flat=True))
    submission_status = "Not Done"
    if chapter and chapter.mandatory:
        submission = Submission.objects.filter(
            profile_id=request.user.profile.id,
            collection_id=collection_id, 
            course_id=course_id, 
            section_id=section_id, 
            chapter_id=chapter_id)
        if submission:
            submission_status = submission[0].status

    
    if user_can_access_collection(request.user, collection):
        return render(request, 'section.html', context={
            'collection': collection,
            'section': section,
            'course': course,
            'chapter': chapter,
            'done_chapters': done_chapters,
            # 'progress': calculate_section_progress(request.user, section),
            'submission_status':submission_status
        })
    else:
        return redirect('/restricted/')

@login_required(login_url=LOGIN_URL)
def collection(request, collection_id, course_id=None):
    collection = Collection.objects.filter(id=collection_id).first()
    if user_can_access_collection(request.user, collection):
        return render(request, 'collection.html', {'collection': collection, 'course_id':course_id})
    else:
        return redirect('courses_app:collections')

@login_required(login_url=LOGIN_URL)
def collections(request):
    if request.user.profile.program:
        trophies = calculate_awarded_trophies(request.user)
    else:
        trophies = None    
    return render(request, 'collections.html', {
        'collections': get_user_collections(request.user), 
        'trophies': trophies})


@login_required
def completed_chapter(request):
    user_profile = request.user.profile
    chapter_id = request.POST.get('chapter_id')
    section_id = request.POST.get('section_id')
    chapter = Chapter.objects.get(id=chapter_id)
    if chapter in user_profile.done_chapters.all():
        done_chapter = Program_Done_Chapters.objects.filter(profile = user_profile, program = user_profile.program, chapter = chapter)
        done_chapter.delete()
    else:
        done_chapter = Program_Done_Chapters(profile = user_profile, program = user_profile.program, chapter = chapter)
        done_chapter.save()

    section_done_points, section_total_points = calculate_section_progress(request.user, Section.objects.get(id=section_id))
    progress = ceil(100*section_done_points / section_total_points) if section_total_points > 0 else -1

    return JsonResponse({'code': 200, 'progress':progress})


@login_required
def submit_chapter(request):
    data = json.loads(request.body)

    profile = request.user.profile
    chapter_id = data['chapter_id']
    program = request.user.profile.program

    try:
        obj, created = Submission.objects.update_or_create(
            profile=request.user.profile, 
            program=request.user.profile.program, 
            collection_id=data['collection_id'],
            course_id=data['course_id'],
            section_id=data['section_id'],
            chapter_id=data['chapter_id'],
            
            defaults = {
                'url':data['exercise_url'],
                'difficulty': data['difficulty'],
                'clarity': data['clarity'],
                'relevance': data['relevance'],
                'time_taken': data['time_taken'],
                'comment': data['comment'],
                'status':'Pending'
            }
        )
    except Exception as e:
        print(e)
        
    return JsonResponse({'code': 200})

@login_required
def update_submission(request):
    data = json.loads(request.body)
    status = data['status']
    profile = Profile.objects.get(id=data['profile_id'])
    program = profile.program
    chapter = Chapter.objects.get(id=data['chapter_id'])
    try:
        submission = Submission.objects.get(
            profile=profile,
            program=program,
            chapter=chapter
        )
        submission.status = status
        submission.save()

        # UPDATE DONE CHAPTERS   
        if status == 'Pass':
            _ , _ = Program_Done_Chapters.objects.update_or_create(
                profile=profile, program=program, chapter=chapter
            )
        if status == 'Redo':
            done_chapter = Program_Done_Chapters.objects.filter(
                profile=profile, program=program, chapter=chapter
            ).delete()

        return JsonResponse({'code': 200, 'status':status})

    except Exception as e:
        print(e)
        return JsonResponse({'code': 500})


@login_required(login_url=LOGIN_URL)
def daily_submissions(request, collection_id, course_id, section_id):

    # This will show all submissions per section FOR EVERY PROGAM. (past programs)   
    # TODO: Need to show submissions on a particular section for a particular program!

    collection = Collection.objects.get(id=collection_id)
    course = Course.objects.get(id=course_id)
    section = Section.objects.get(id=section_id)
    submissions = Submission.objects.filter(
        collection_id=collection_id, 
        course_id=course_id, 
        section_id=section_id
    ).order_by("profile__user__last_name", 'chapter')

    user_groups_queryset = request.user.groups.values_list('name',flat = True)
    user_groups = list(user_groups_queryset)  
    if 'admin' not in user_groups and 'teacher' not in user_groups and 'checker' not in user_groups:
        return redirect('/restricted/')
    
    return render(request, 'section.html', context={
            'collection': collection,
            'section': section,
            'course': course,
            'chapter': None,
            'done_chapters': None,
            'submissions': submissions,
            'submissions_page': True
    })





def paths(request):
    return render(request, 'paths.html')
