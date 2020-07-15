from django.shortcuts import render, redirect
from courses_app.models import Course, Section, Chapter, Collection, CollectionCourse, CourseAccess, CourseAccessCollection

from django.contrib.auth.decorators import login_required, user_passes_test
from profile_app.models import user_can_access_collection, get_user_collections, Program_Done_Chapters
from django.http import JsonResponse
from django.db.models import F, Sum


@login_required()
def section(request, collection_id, course_id, section_id, chapter_id=None):
    collection = Collection.objects.get(id=collection_id)
    course = Course.objects.get(id=course_id)
    section = Section.objects.get(id=section_id)
    chapter = None if chapter_id is None else Chapter.objects.get(id=chapter_id)
    done_chapters = list(Program_Done_Chapters.objects.filter(profile=request.user.profile, program=request.user.profile.program).values_list('chapter', flat=True))

    if user_can_access_collection(request.user, collection):
        return render(request, 'section.html', context={
            'collection': collection,
            'section': section,
            'course': course,
            'chapter': chapter,
            'done_chapters': done_chapters
        })
    else:
        return redirect('/restricted/')

@login_required()
def collection(request, collection_id, course_id=None):
    collection = Collection.objects.filter(id=collection_id).first()
    if user_can_access_collection(request.user, collection):
        return render(request, 'collection.html', {'collection': collection, 'course_id':course_id})
    else:
        return redirect('courses_app:collections')

@login_required()
def collections(request):
    return render(request, 'collections.html', {'collections': get_user_collections(request.user)})


@login_required
# @user_passes_test(can_view_course, login_url='/welcome/')
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