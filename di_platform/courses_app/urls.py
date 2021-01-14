from django.urls import path
from . import views

app_name = 'courses_app'

urlpatterns = [
    path('', views.collections, name='collections'),
    path('collection/<int:collection_id>/', views.collection, name='collection'),
    path('collection/<int:collection_id>/course/<int:course_id>', views.collection, name='course'),

    path('collection/<int:collection_id>/course/<int:course_id>/section/<int:section_id>', views.section, name='section'),
    path('collection/<int:collection_id>/course/<int:course_id>/section/<int:section_id>/chapter/<int:chapter_id>', views.section, name='chapter'),

    path('completed_chapter/', views.completed_chapter, name='completed_chapter'),

    path('submit_chapter/', views.submit_chapter, name='submit_chapter'),
    path('update_submission/', views.update_submission, name='update_submission'),
    
    path('collection/<int:collection_id>/course/<int:course_id>/section/<int:section_id>/daily_submissions/', views.daily_submissions, name='daily_submissions'),


    path('paths/', views.paths, name='paths'),

]
