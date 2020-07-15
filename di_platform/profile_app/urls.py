from django.urls import path
from . import views

app_name = 'profile_app'

urlpatterns = [
  path('', views.profile, name='profile'),
  path('edit/', views.edit, name='profile-edit'),
  path('edit/profile_picture', views.edit_profile_picture, name='edit_profile_picture'),
  path('signup/', views.signup, name='signup'),
  path('login/', views.login_auth, name='login'),
  path('logout/', views.logout_auth, name='logout'),
]