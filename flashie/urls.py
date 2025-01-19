from django.urls import path
from . import views

app_name = 'flashie'

urlpatterns = [
    path('', views.home, name='home'),
    path('upload-pdf/', views.upload_pdf, name='upload_pdf'),
    path('extract-video-script/', views.extract_video_script, name='extract_video_script'),
] 