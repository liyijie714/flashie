from django.urls import path
from . import views

app_name = 'grader'

urlpatterns = [
    path('', views.home, name='home'),
] 