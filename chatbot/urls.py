from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('api/send_message/', views.send_message, name='send_message'),
    path('api/save_role/', views.save_role, name='save_role'),
    path('api/get_roles/', views.get_roles, name='get_roles'),
    path('api/get_chat_history/<int:role_id>/', views.get_chat_history, name='get_chat_history'),
    path('debug/models/', views.debug_models, name='debug_models'),
    path('api/create_role/', views.create_role, name='create_role'),
]