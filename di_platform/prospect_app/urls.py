from django.urls import path
from . import views

app_name = 'prospect_app'

urlpatterns = [
  path('', views.dashboard, name=''),
  path('intro-html-css/', views.intro_html_css, name='intro-html-css'),
  path('intro-fullstack-js/', views.intro_fullstack_js, name='intro-fullstack-js'),
  path('intro-fullstack-python/', views.intro_fullstack_python, name='intro-fullstack-python'),
  path('dashboard/', views.dashboard, name='dashboard'),
  path('apply/', views.apply, name='apply'),
  path('pricing/', views.pricing, name='pricing'),
  path('terms/', views.terms, name='terms'),
  path('privacy/', views.privacy, name='privacy'),

]