from django.shortcuts import render, redirect
from courses_app.models import *

from django.contrib.auth.decorators import login_required, user_passes_test
from profile_app.models import user_can_access_collection, get_user_collections, Program_Done_Chapters, Profile
from django.http import JsonResponse
from django.db.models import F, Sum
from di_platform.settings import LOGIN_URL
import json


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
    return render(request, 'collections.html', {'collections': get_user_collections(request.user)})


@login_required
def completed_chapter(request):
    user_profile = request.user.profile
    chapter_id = request.POST.get('chapter_id')
    chapter = Chapter.objects.get(id=chapter_id)

    if chapter in user_profile.done_chapters.all():
        done_chapter = Program_Done_Chapters.objects.filter(profile = user_profile, program = user_profile.program, chapter = chapter)
        done_chapter.delete()
    else:
        done_chapter = Program_Done_Chapters(profile = user_profile, program = user_profile.program, chapter = chapter)
        done_chapter.save()

    return JsonResponse({'code': 200})


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


# JMS


def test(request):
    collections = Collection.objects.all()
    for collection in collections:
        print("COLLECTION")
        print(collection)
        collectioncourses = collection.collectioncourse_set.all()
        for collectioncourse in collectioncourses:
            course = collectioncourse.course
            print("COURSE")
            print(course)
            coursesections = course.coursesection_set.all()
            for coursesection in coursesections:
                section = coursesection.section
                print("SECTION")
                print(section)
                sectionchapters = section.sectionchapter_set.all()
                for sectionchapter in sectionchapters:
                    chapter = sectionchapter.chapter
                    print("CHAPTER")
                    print(chapter)
            

    return render(request, 'test.html', {'collections': collections })


def test2(request):
    collection = Collection.objects.get(id=1)
    #all courses belonging to collection 1
    courses = collection.courses.all()

    course1 = Course.objects.get(id=1)
    course1.collectioncourse_set.get(collection_id=2).collection.title

    # courses2 = Course.objects.filter(collection=collection_id).all()
    print(courses)
    
    return render(request, 'test.html', {'collections': collection })


# JMS END