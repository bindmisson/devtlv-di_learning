from django.db import models
from martor.widgets import AdminMartorWidget
from django.contrib import admin
from courses_app.models import Course, Section, Chapter, Collection, CourseAccess
from courses_app.models import SectionChapter, CourseSection, CollectionCourse, CourseAccessCollection


class SectionChapterInline(admin.TabularInline):
    model = SectionChapter

class CourseSectionInline(admin.TabularInline):
    model = CourseSection    

class CollectionCourseInline(admin.TabularInline):
    model = CollectionCourse

class CourseAccessInline(admin.TabularInline):
    model = CourseAccessCollection   




class CollectionAdmin(admin.ModelAdmin):
  list_display = ('title', 'total_weeks')
  list_editable = ('total_weeks',)
  inlines = [CollectionCourseInline]

class CourseAdmin(admin.ModelAdmin):
  formfield_overrides = {
    models.TextField: { 'widget': AdminMartorWidget },
  }
  list_display = ('title', 'description')
  list_editable = ('description',)
  inlines = [CourseSectionInline]

class SectionAdmin(admin.ModelAdmin):
  formfield_overrides = {
    models.TextField: { 'widget': AdminMartorWidget },
  }
  list_display = ('title', 'description', 'short_description')
  list_editable = ('description', 'short_description')
  inlines = [SectionChapterInline]

class ChapterAdmin(admin.ModelAdmin):
  formfield_overrides = {
    models.TextField: { 'widget': AdminMartorWidget },
  }
  list_display = ('title', 'group', 'points_value', 'mandatory')
  list_editable = ('group', 'points_value', 'mandatory')


class CourseAccessAdmin(admin.ModelAdmin):
  list_display = ('name',)
  inlines = [CourseAccessInline]



admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(CourseAccess, CourseAccessAdmin)
