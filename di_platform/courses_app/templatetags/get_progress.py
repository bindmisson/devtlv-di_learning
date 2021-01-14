from django import template
from courses_app.views import calculate_section_progress
from math import ceil

register = template.Library() 

@register.filter(name='get_section_progress') 
def get_section_progress(user, section):
    section_done_points, section_total_points = calculate_section_progress(user, section)
    # If section has no points, return -1.  Templates will not show progress bar if negative
    return ceil(100*section_done_points / section_total_points) if section_total_points > 0 else -1
    
    

@register.filter(name='get_course_progress') 
def get_course_progress(user, course):
    course_done_points = 0
    course_total_points = 0
    
    sections = course.sections.all()
    for section in sections:
        section_done_points, section_total_points = calculate_section_progress(user, section)
        course_done_points += section_done_points
        course_total_points += section_total_points

    # If course has no points, return -1.  Templates will not show progress bar if negative
    return ceil(100*course_done_points / course_total_points) if course_total_points > 0 else -1


@register.filter(name='get_collection_progress') 
def get_collection_progress(user, collection):
    collection_done_points = 0
    collection_total_points = 0
    
    courses = collection.courses.all()
    for course in courses:
        sections = course.sections.all()

        for section in sections:
            section_done_points, section_total_points = calculate_section_progress(user, section)
            collection_done_points += section_done_points
            collection_total_points += section_total_points

    # If course has no points, return -1.  Templates will not show progress bar if negative
    return ceil(100*collection_done_points / collection_total_points) if collection_total_points > 0 else -1