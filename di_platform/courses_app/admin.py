from django.db import models
from martor.widgets import AdminMartorWidget
from django.contrib import admin
from courses_app.models import Course, Section, Chapter, Collection, CourseAccess
from courses_app.models import SectionChapter, CourseSection, CollectionCourse, CourseAccessCollection, TrophyRequirements


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
    fields = ('chapter', 'chapter_points_value', 'chapter_group', 'chapter_tags', 'sort', )
    readonly_fields = ['chapter_points_value', 'chapter_tags', 'chapter_group']

    def chapter_points_value(self, obj):
      return obj.chapter.points_value
    
    def chapter_tags(self, obj):
      return obj.chapter.tags
    
    def chapter_group(self, obj):
      return obj.chapter.group
    

class CourseAccessInline(admin.TabularInline):
    model = CourseAccessCollection   



class CollectionAdmin(admin.ModelAdmin):
  list_display = ('id', 'title', 'description','total_weeks')
  list_display_links = ('title',)
  list_editable = ('total_weeks',)
  search_fields = ['id', 'title','tags']
  inlines = [CollectionCourseInline]


class CourseAdmin(admin.ModelAdmin):
  formfield_overrides = {
    models.TextField: { 'widget': AdminMartorWidget },
  }
  list_display = ('id', 'title', 'tags', 'description')
  list_display_links = ('title',)
  list_editable = ('tags',)
  search_fields = ['id', 'title','tags']
  inlines = [CourseSectionInline]

class SectionAdmin(admin.ModelAdmin):
  formfield_overrides = {
    models.TextField: { 'widget': AdminMartorWidget },
  }
  list_display = ('id', 'title', 'tags', 'short_description', 'description')
  list_display_links = ('title',)
  list_editable = ('tags', 'short_description')
  search_fields = ['id', 'title','tags']
  inlines = [SectionChapterInline]

class ChapterAdmin(admin.ModelAdmin):
  formfield_overrides = {
    models.TextField: { 'widget': AdminMartorWidget },
  }
  ordering = ("title",)
  list_display = ('id', 'title', 'tags', 'group', 'points_value', 'mandatory', 'self_learning', 'advanced')
  list_display_links = ('title',)
  list_editable = ('tags', 'group', 'points_value', 'mandatory', 'self_learning', 'advanced')
  search_fields = ['id', 'title', 'tags']

class CourseAccessAdmin(admin.ModelAdmin):
  list_display = ('name',)
  inlines = [CourseAccessInline]


admin.site.register(TrophyRequirements)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(CourseAccess, CourseAccessAdmin)
