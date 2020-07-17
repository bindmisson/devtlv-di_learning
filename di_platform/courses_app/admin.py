from django.db import models
from martor.widgets import AdminMartorWidget
from django.contrib import admin
from courses_app.models import Course, Section, Chapter, Collection, CourseAccess
from courses_app.models import SectionChapter, CourseSection, CollectionCourse, CourseAccessCollection


class CollectionCourseInline(admin.TabularInline):
    model = CollectionCourse
    fields = ('course', 'course_tags', 'sort', )
    readonly_fields = ['course_tags']

    def course_tags(self, obj):
      return obj.course.tags

class CourseSectionInline(admin.TabularInline):
    model = CourseSection    
    fields = ('section', 'section_tags', 'sort', )
    readonly_fields = ['section_tags']

    def section_tags(self, obj):
      return obj.section.tags

class SectionChapterInline(admin.TabularInline):
    model = SectionChapter
    fields = ('chapter', 'chapter_group', 'chapter_tags', 'sort', )
    readonly_fields = ['chapter_tags', 'chapter_group']

    def chapter_tags(self, obj):
      return obj.chapter.tags
    
    def chapter_group(self, obj):
      return obj.chapter.group

class CourseAccessInline(admin.TabularInline):
    model = CourseAccessCollection   



class CollectionAdmin(admin.ModelAdmin):
  list_display = ('title', 'description','total_weeks', 'jms')
  list_editable = ('total_weeks',)
  inlines = [CollectionCourseInline]

  def jms(self, obj):
    item = [''] if obj.topics is None else obj.topics.split(',')
    print(type(item))
    return item[0]

class CourseAdmin(admin.ModelAdmin):
  formfield_overrides = {
    models.TextField: { 'widget': AdminMartorWidget },
  }
  list_display = ('title', 'tags', 'description')
  list_editable = ('tags',)
  inlines = [CourseSectionInline]

class SectionAdmin(admin.ModelAdmin):
  formfield_overrides = {
    models.TextField: { 'widget': AdminMartorWidget },
  }
  list_display = ('title', 'tags', 'short_description', 'description')
  list_editable = ('tags', 'short_description')
  inlines = [SectionChapterInline]

class ChapterAdmin(admin.ModelAdmin):
  formfield_overrides = {
    models.TextField: { 'widget': AdminMartorWidget },
  }
  list_display = ('title', 'tags', 'group', 'points_value', 'mandatory', 'description')
  list_editable = ('tags', 'group', 'points_value', 'mandatory')

class CourseAccessAdmin(admin.ModelAdmin):
  list_display = ('name',)
  inlines = [CourseAccessInline]



admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(CourseAccess, CourseAccessAdmin)