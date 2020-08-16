from django import forms
from django.contrib.auth.models import User
from profile_app.models import Profile


class ProfileEditForm(forms.ModelForm):
  class Meta:
    model   = Profile
    fields  = ('linkedin', 'github', 'bio', 'code_formatting')
    widgets = {
      'linkedin': forms.URLInput(attrs={
        'id': 'profile-edit-linkedin',
        'class': 'form-control',
        'placeholder': 'LinkedIn',
        'required': False
      }),
      'github': forms.URLInput(attrs={
        'id': 'profile-edit-github',
        'class': 'form-control',
        'placeholder': 'Github',
        'required': False
      }),
      'bio': forms.Textarea(attrs={
        'id': 'profile-edit-bio',
        'class': 'form-control',
        'placeholder': 'Bio',
        'required': False
      }),
      'code_formatting': forms.Select(attrs={
        'id': 'profile-edit-code_formatting',
        'class': 'form-control',
        'required': True,
        'blank': False
      }),
    }


class ProfilePictureUploadForm(forms.Form):
  image = forms.ImageField(label='')


class UserEditForm(forms.ModelForm):
  class Meta:
    model   = User
    fields  = ('first_name', 'last_name', 'email')
    widgets = {
      'first_name': forms.TextInput(attrs={
        'id': 'signup-first-name',
        'class': 'form-control',
        'placeholder': 'first name',
        'required': False
      }),
      'last_name': forms.TextInput(attrs={
        'id': 'signup-last-name',
        'class': 'form-control',
        'placeholder': 'last name',
        'required': False
      }),
      'email': forms.EmailInput(attrs={
        'id': 'signup-email',
        'class': 'form-control',
        'placeholder': 'email',
        'required': False
      }),
    }


class SignupForm(forms.ModelForm):
  class Meta:
    model   = User
    fields  = ('first_name', 'last_name', 'username', 'email', 'password')
    help_texts = { 'username': None }
    widgets = {
      'first_name': forms.TextInput(attrs={
        'id': 'signup-first-name',
        'class': 'form-control',
        'placeholder': 'first name',
        'required': True
      }),
      'last_name': forms.TextInput(attrs={
        'id': 'signup-last-name',
        'class': 'form-control',
        'placeholder': 'last name',
        'required': True
      }),
      'username': forms.TextInput(attrs={
        'id': 'signup-username',
        'class': 'form-control',
        'placeholder': 'username',
        'required': True
      }),
      'email': forms.EmailInput(attrs={
        'id': 'signup-email',
        'class': 'form-control',
        'placeholder': 'email',
        'required': True
      }),
      'password': forms.PasswordInput(attrs={
        'id': 'signup-password',
        'class': 'form-control',
        'placeholder': 'password',
        'required': True
      }),
    }


class LoginForm(forms.ModelForm):
  class Meta:
    model  = User
    fields = ('username', 'password')
    help_texts = { 'username': None }
    widgets = {
      'username': forms.TextInput(attrs={
        'id': 'login-username',
        'class': 'form-control',
        'placeholder': 'username',
        'required': True
      }),
      'password': forms.PasswordInput(attrs={
        'id': 'login-password',
        'class': 'form-control',
        'placeholder': 'password',
        'required': True
      }),
    }
