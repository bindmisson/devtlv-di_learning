from django.contrib import admin
from profile_app.models import Profile, Program
from courses_app.models import Collection, Chapter


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'course_access', 'program')
    list_editable = ('course_access', 'program')
    search_fields = ['user__first_name', 'user__last_name', 'user__username']

    def username(self, obj):
        return f"{obj.user.username}"

    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Program)

# class ProfileData(admin.ModelAdmin):
#     readonly_fields = ('completion_percent', )

#     def completion_percent(self, obj):
#         completion = ''
#         # for collection in Collection.objects.all():
#         #     all_chapters = Chapter.objects.filter(
#         #         section__course__collection=collection)
#         #     done = [chapter for chapter in obj.done_chapters.all()
#         #             if chapter in all_chapters]
#         #     if len(all_chapters) == 0:
#         #         continue
#         #     else:
#         #         completion += f'{collection.title} : {(len(done)/len(all_chapters))*100}% completed \n'

#         return completion

# admin.site.register(Profile, ProfileData)