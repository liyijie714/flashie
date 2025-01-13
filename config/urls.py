from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Include Django's built-in auth URLs
    path('', include('django.contrib.auth.urls')),
    
    # Custom login view
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Your app URLs
    path('chatbot/', include('chatbot.urls')),
    path('flashie/', include('flashie.urls')),
] 