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

    path('paths/', views.paths, name='paths'),

    path('test/', views.test, name='test'),
    path('test2/', views.test2, name='test2'),
]
