from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Profile, CODE_FORMATTING_CHOICES
from .forms import SignupForm, LoginForm, ProfileEditForm, UserEditForm, ProfilePictureUploadForm
from courses_app.models import CourseAccess
from django.contrib.messages import get_messages
from di_platform.settings import LOGIN_URL
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from django.contrib.auth.password_validation import validate_password
from .mailers import reset_password_email, welcome_email
from .tokens import account_activation_token


@login_required(login_url=LOGIN_URL)
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


@login_required(login_url=LOGIN_URL)
# @user_passes_test(can_view_course, login_url='/welcome/')
def edit(request):
    profile = request.user.profile

    if request.method == 'POST':
        profile.bio = request.POST.get('bio')
        profile.mobile = request.POST.get('mobile')
        profile.linkedin = request.POST.get('linkedin')
        profile.github = request.POST.get('github')
        profile.code_formatting = request.POST.get('code_formatting')
        profile.save()

        request.user.first_name = request.POST.get('first_name')
        request.user.last_name  = request.POST.get('last_name')
        request.user.email  = request.POST.get('email')
        request.user.save()

        return redirect('profile_app:profile')

    profile_edit_form = ProfileEditForm(initial={
        'github': profile.github,
        'linkedin': profile.linkedin,
        'bio': profile.bio,
        'code_formatting': profile.code_formatting,
        'mobile': profile.mobile
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


@login_required(login_url=LOGIN_URL)
def profile(request):

    for code_format in CODE_FORMATTING_CHOICES:
        if code_format[0] == request.user.profile.code_formatting:
            code_format_value = code_format[1]

    return render(request, 'profile.html', context={
        'profile': request.user.profile,
        'code_format_value': code_format_value
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
            user.profile.mobile = request.POST.get('mobile')
            user.profile.save()
            login(request, user)
            welcome_email(user)
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


@login_required(login_url=LOGIN_URL)
def logout_auth(request):
    logout(request)
    return redirect('profile_app:login')


def password_change_error(request, message='Sorry, something went wrong, please try again.'):
    messages.add_message(request, messages.ERROR, message)
    return redirect('profile_app:password_reset_final')


def reset_password_step1(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST.get('email'))

        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.add_message(request, messages.ERROR, 'Email does not exist in our system.')
            return redirect('profile_app:start_password_reset')

        reset_password_email(request, user)
        return render(request, 'check_your_inbox.html')

    return render(request, 'email_reset_step_one.html')


def reset_password_step2(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        request.session['user_pk'] = user.pk
        return redirect('profile_app:password_reset_final')
    else:
        messages.add_message(request, messages.ERROR, 'Seems like something went wrong, try again!')
        return redirect('profile_app:start_password_reset')


def reset_password_step3(request):
    if request.method == "POST":
        password = request.POST.get('password')
        user = User.objects.get(pk=request.session['user_pk'])

        try:
            password == request.POST.get('confirmpassword')
        except:
            return password_change_error(request=request, message='Passwords did not match.')

        try:
            validate_password(password, user=User)
        except:
            return password_change_error(request=request, message='Password did not meet minimum security requirements.')

        user.set_password(password)
        user.save()
        return redirect('profile_app:login')

    return render(request, 'reset_password_final.html')
