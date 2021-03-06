import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.auth import user_logged_in

from io import BytesIO
from PIL import Image
from django.core.files import File
from courses_app.models import Collection, Chapter, CourseAccess
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.db.models import F, Sum
from django.db.models.functions import Coalesce




def get_user_collections(user):
    """
    Returns collections for logged in user. 
    For regular users, this is sorted by their course_access.
    For admins (who don't have a course_access), this is sorted alphabetically by title.
    """
    if user.groups.filter(name__in=['admin']).exists():
        return Collection.objects.all().order_by('title')

    course_access = user.profile.course_access
    try:
        return user.profile.course_access.collections.all().order_by("courseaccesscollection__sort")
    except:
        return []


def user_can_access_collection(user, collection):
    if user.groups.filter(name__in=['admin']).exists():
        return True

    return collection in get_user_collections(user)


def content_file_name(instance, filename=''):
    return '/'.join(['staticfiles/media/profile_pictures', "{}_{}".format(instance.user.id, instance.user.username), filename])


def compress(image):
    im = Image.open(image)
    im = im.convert('RGB')
    im_io = BytesIO()
    im.save(im_io, 'JPEG', quality=70)
    new_image = File(im_io, name=image.name)
    return new_image


def can_take_attendance(user):
    return user.groups.filter(name__in=['admin', 'teacher']).exists()


class Program(models.Model):
    name = models.CharField(max_length=100)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, blank=True, null=True)
    link = models.URLField(max_length=200, blank=True, null=True)
    calendar = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return self.name

CODE_FORMATTING_CHOICES = [
    ('color-brewer', 'Default'),
    ('monokai-sublime', 'Monokai Sublime'),
    ('mono-blue', 'Mono Blue'),
    ('vs', 'VS'),
    ('atom-one-dark', 'Atom One Dark'),
    ('atom-one-light', 'Atom One Light'),
    ('zenburn', 'Zen Burn'),
    ('agate', 'Agate'),
    ('androidstudio', 'Android Studio'),
    ('darcula', 'Darcula'),
    ('rainbow', 'Rainbow'),
    ('solarized-dark', 'Solarized Dark'),
    ('solarized-light', 'Solarized Light'),
    ('github', 'Github'),
    ('railscasts', 'Rails Casts'),
    ('tomorrow', 'Tomorrow'),
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    linkedin = models.CharField(max_length=264, blank=True, null=True)
    github = models.CharField(max_length=264, blank=True, null=True)
    done_chapters = models.ManyToManyField('courses_app.Chapter', through="Program_Done_Chapters", related_name='done_by', blank=True)
    profile_picture = models.ImageField(default='', upload_to=content_file_name, null=True, blank=True)
    points_total = models.IntegerField(default=0, editable=False)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, blank=True, null=True)
    course_access = models.ForeignKey(CourseAccess, on_delete=models.CASCADE, blank=True, null=True)
    bonus_points = models.IntegerField(default=0)
    code_formatting = models.CharField(max_length=200, choices=CODE_FORMATTING_CHOICES, blank=False, default='color-brewer')

    def get_image_name(self, path):
        return os.path.basename(path) 

    def update_profile_picture(self, old_image_path):
        old_image_name = self.get_image_name(old_image_path)
        new_image_name = self.get_image_name(str(self.profile_picture))

        filename = content_file_name(self, new_image_name)
        tocheck = '/'.join(['staticfiles/media/profile_pictures', "{}_{}".format(self.user.id, self.user.username), old_image_name])
        if os.path.isfile(tocheck):
            os.remove(tocheck)
            new_image = compress(self.profile_picture)
            self.profile_picture = new_image

    def get_profile_picture(self):
        filename = self.get_image_name(str(self.profile_picture))
        path = content_file_name(self, filename)
        if os.path.isfile(os.path.join(path)):
            return path.replace("staticfiles",'')

        return 'theme/images/avatars/home-profile.jpg'
        

    def __repr__(self):
        return '<Profile {}>'.format(self.user.username)

    def __str__(self):
        return self.user.username


class Program_Done_Chapters(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    chapter = models.ForeignKey('courses_app.Chapter', on_delete=models.CASCADE)

    # I want to add this, but can't be sure that there arent legacy users with duplicates..(there probably are...)
    # class Meta:
    #     unique_together = ('profile', 'program', 'chapter')

    def __repr__(self):
        return f"<done chapter> id: {self.chapter.id}, title: {self.chapter.title}, profile: {self.profile.id}, program: {self.program.id}" 



@receiver(m2m_changed, sender=Profile.done_chapters.through)
def done_chapters_changed(sender, **kwargs):
    instance = kwargs.pop('instance', None)
    action = kwargs.pop('action', None)
    pk = next(iter(kwargs.pop('pk_set', None)))
    
    if isinstance(instance, Profile):
        profile = instance
    elif isinstance(instance, Chapter): 
        profile = Profile.objects.get(id=pk)  

    if action == "post_add" or action == "post_remove":
        profile.points_total = Coalesce(Chapter.objects.filter(done_by=profile).aggregate(Sum('points_value'))['points_value__sum'], 0)
        profile.save()


# UserSession and remove_other_sessions
# Designed to prevent multiple logins on the same account.
# https://stackoverflow.com/questions/50833980/how-to-prevent-multiple-login-in-django

class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.OneToOneField(Session, on_delete=models.CASCADE)

@receiver(user_logged_in)
def remove_other_sessions(sender, user, request, **kwargs):
    Session.objects.filter(usersession__user=user).delete()
    request.session.save()
    UserSession.objects.get_or_create(
        user=user,
        session=Session.objects.get(pk=request.session.session_key)
    )