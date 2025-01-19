from django.urls import path
from . import views

app_name = 'flashie'

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('audio/<int:pdf_id>/', views.serve_audio, name='serve_audio'),
    path('pdf/<int:pdf_id>/', views.serve_pdf, name='serve_pdf'),
] 