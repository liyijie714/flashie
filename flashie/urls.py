from django.urls import path
from . import views

app_name = 'flashie'

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('audio/<int:pdf_id>/', views.serve_audio, name='serve_audio'),
    path('pdf/<int:pdf_id>/', views.serve_pdf, name='serve_pdf'),
    path('lecture/upload/', views.upload_lecture, name='upload_lecture'),
    path('lecture/list/', views.lecture_list, name='lecture_list'),
    path('lecture/<int:lecture_id>/view/', views.lecture_viewer, name='lecture_viewer'),
    path('lecture/<int:lecture_id>/file/<str:file_type>/', views.serve_lecture_file, name='serve_lecture_file'),
] 