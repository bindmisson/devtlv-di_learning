from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from profile_app.models import Profile
from profile_app.forms import SignupForm, LoginForm, ProfileEditForm, UserEditForm, ProfilePictureUploadForm
from courses_app.models import CourseAccess
from django.contrib.messages import get_messages


@login_required()
# @user_passes_test(can_view_course, login_url='/welcome/')
def edit_profile_picture(request):
  profile_id = request.user.profile.id
  if request.method == 'POST':
    form = ProfilePictureUploadForm(request.POST, request.FILES)
    if form.is_valid():
      profile = Profile.objects.get(id=profile_id)
      old_image_path = str(profile.profile_picture)
      profile.profile_picture = form.cleaned_data['image']
      profile.update_profile_picture(old_image_path)
      profile.save()
      
  return redirect( 'profile_app:profile-edit' )


@login_required()
# @user_passes_test(can_view_course, login_url='/welcome/')
def edit(request):
  profile = request.user.profile

  if request.method == 'POST':
    profile.bio = request.POST.get('bio')
    profile.linkedin = request.POST.get('linkedin')
    profile.github = request.POST.get('github')
    profile.save()

    request.user.first_name = request.POST.get('first_name')
    request.user.last_name  = request.POST.get('last_name')
    request.user.email  = request.POST.get('email')
    request.user.save()

    return redirect('profile_app:profile')

  profile_edit_form = ProfileEditForm(initial={
    'github': profile.github,
    'linkedin': profile.linkedin,
    'bio': profile.bio
  })

  user_edit_form = UserEditForm(initial={
    'first_name': profile.user.first_name,
    'last_name': profile.user.last_name,
    'email': profile.user.email,
    'profile_picture': profile.profile_picture
  })

  return render(request, 'profile_edit.html', context={
    'profile_edit_form': profile_edit_form,
    'user_edit_form': user_edit_form,
    'user_profile_pic_form': ProfilePictureUploadForm()
  })


@login_required()
# @user_passes_test(can_view_course, login_url='/welcome/')
def profile(request):
  profile = Profile.objects.get(id=request.user.profile.id)
  return render(request, 'profile.html', context={
    'profile': profile,
  })


def signup(request):
  if request.user.is_authenticated:
    return redirect('/')

  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')

    try:
      User.objects.create_user(
        username=username,
        password=password,
        first_name=request.POST.get('first_name'),
        last_name=request.POST.get('last_name'),
        email=request.POST.get('email')
      )
    except IntegrityError:
      messages.error(request, 'Sorry, username already taken')
      return redirect('/profile/signup/')

    user = authenticate(request, username=username, password=password)
    if user is not None:
      Profile.objects.get_or_create(user=user)
      user.profile.course_access = CourseAccess.objects.get(name="new")
      user.profile.save()
      login(request, user)
      return redirect('courses_app:collections')
    else:
      messages.error(request, 'Something went wrong, please try again')
      return redirect('profile_app:signup')

  return render(request, 'signup.html', context={ 'signup_form': SignupForm(request.POST) })


def login_auth(request):
  if request.user.is_authenticated:
    return redirect('/')

  if request.method == 'POST':
    user = authenticate(
      request,
      username=request.POST.get('username'),
      password=request.POST.get('password')
    )

    if user is not None:
      login(request, user)
      next = request.GET.get('next', '/')
      return redirect(f'{next}')
    else:
      messages.error(request, 'Username or Password Incorrect')
      # storage = get_messages(request)
      # for message in storage:
      #   print(message)
      return redirect('profile_app:login')

  return render(request, 'login.html', context={ 'login_form': LoginForm(request.POST) })


@login_required()
# @user_passes_test(can_view_course, login_url='/welcome/')
def logout_auth(request):
  logout(request)
  return redirect('profile_app:login')
