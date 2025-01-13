from django.contrib import admin
from django.urls import path, include
from . import views
app_name = 'products' 
urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create, name='create'),
    path('<int:product_id>/', views.detail, name='detail'),
    path('edit/<int:product_id>/', views.edit, name='edit'),
    path('delete/<int:product_id>/', views.delete, name='delete'),
    path('<int:product_id>/upvote', views.upvote, name='upvote'),
]
