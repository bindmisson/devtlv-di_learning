import os

from django.conf import settings
from django.db import models


class Chapter(models.Model):
    GROUP_CHOICES = [
        ('XP', 'XP'),
        ('XPG', 'XP Gold'),
        ('XPN', 'XP Ninja'),
        ('HW', 'Homework'),
        ('RF', 'Refresher'),
        ('RL', 'Remote Learning'),
        ('MP', 'Mini Project'),
        ('SR', 'Survey'),
        ('DC', 'Daily Challenge'),
        ('CO', 'Course')
    ]
    title = models.CharField(max_length=38, default='', help_text="(Max 38 Characters)")
    tags = models.CharField(max_length=100, default='', null=True, blank=True, help_text="So admins can identify chapters better")
    group = models.CharField(max_length=20, choices=GROUP_CHOICES, default='XP')
    points_value = models.IntegerField(null=True, blank=True, default=5)
    mandatory = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True, default='')
    text = models.TextField(null=True, blank=True, default='')
    code = models.TextField(null=True, blank=True, default='')
    exercise = models.TextField(null=True, blank=True, default='')
    enabled = models.BooleanField(default=True)

    def __repr__(self):
        return f'<Chapter {self.title}>'

    def __str__(self):
        return self.title + (f' <TAGS> {self.tags}' if self.tags else '')


class Section(models.Model):
    title = models.CharField(max_length=264, default='')
    tags = models.CharField(max_length=100, default='', null=True, blank=True, help_text="So admins can identify sections better")
    thumbnail = models.ImageField(default='default.jpg', upload_to='images/thumbnails/section', null=True, blank=True)
    short_description = models.CharField(max_length=60, default='', help_text="(Max 60 Characters)")
    description = models.TextField(default='', null=True, blank=True)
    chapters = models.ManyToManyField(Chapter, blank=True, related_name="sections", through='SectionChapter')
    enabled = models.BooleanField(default=True)

    def __repr__(self):
        return f'<Section {self.title}>'

    def __str__(self):
        return self.title + (f' <TAGS> {self.tags}' if self.tags else '')

    def get_thumbnail(self):
        image_path = str(self.thumbnail)
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, image_path)):
            return image_path

        return 'theme/images/course/1.png'


class Course(models.Model):
    title = models.CharField(max_length=264, default='')
    tags = models.CharField(max_length=100, default='', null=True, blank=True, help_text="So admins can identify courses better")
    thumbnail = models.ImageField(default='', upload_to='images/thumbnails/course', null=True, blank=True)
    description = models.TextField(default='', null=True, blank=True)
    sections = models.ManyToManyField(Section, blank=True, related_name="courses", through='CourseSection')
    enabled = models.BooleanField(default=True)

    def __repr__(self):
        return f'<Course {self.title}>'

    def __str__(self):
        return self.title + (f' <TAGS> {self.tags}' if self.tags else '')

    def get_thumbnail(self):
        image_path = str(self.thumbnail)
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, image_path)):
            return image_path

        return 'theme/images/course/1.png'

    def get_tags(self):
        return f' <Tags> {self.tags}'

class Collection(models.Model):
    title = models.CharField(max_length=264, default='')
    topics = models.CharField(max_length=264, default='', blank=True, null=True, help_text="CSV list - Max 12 items")
    total_weeks = models.IntegerField(default=12)
    thumbnail = models.ImageField(default='default.jpg', upload_to='images/thumbnails/collection', null=True, blank=True)
    description = models.TextField(default='', null=True, blank=True)
    courses = models.ManyToManyField(Course, blank=True, related_name="collections", through="CollectionCourse")
    enabled = models.BooleanField(default=True)

    
    def __repr__(self):
        return f'<Collection {self.title}>'

    def __str__(self):
        return self.title

    def get_thumbnail(self):
        image_path = str(self.thumbnail)
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, image_path)):
            return image_path

        return 'theme/images/course/1.png'


        


# INTERMEDIATE TABLES

class SectionChapter(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    sort = models.IntegerField(blank=True, default=0)

class CourseSection(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    sort = models.IntegerField(blank=True, default=0)

class CollectionCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    sort = models.IntegerField(blank=True, default=0)



# COURSE ACCESS GROUPS

class CourseAccess(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    collections = models.ManyToManyField(Collection, blank=True, through="CourseAccessCollection")

    def __repr__(self):
        return f'<CourseAccess {self.name}>'

    def __str__(self):
        return self.name

class CourseAccessCollection(models.Model):
    course_access = models.ForeignKey(CourseAccess, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    sort = models.IntegerField(blank=True, default=0)