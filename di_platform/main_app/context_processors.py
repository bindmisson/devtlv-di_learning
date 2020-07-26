from courses_app import models as course_models
from main_app import models as main_models
from profile_app import models as profile_models
from django.contrib.auth.decorators import login_required, user_passes_test
from profile_app.models import Profile


def get_user_global_info(request):
    pass
    profile, collections, completion = None, None, None
    if request.user.is_authenticated:
        profile = profile_models.Profile.objects.get(user=request.user)
        collections = course_models.Collection.objects.all()
        completion = {}
    return {
        'global_profile': profile,
        'global_collections': collections,
        'global_completion': completion,

    }


