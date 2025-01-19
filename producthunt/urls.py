from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from flashie import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('flashie.urls', namespace='flashie')),
    path('accounts/', include('accounts.urls')),
    path('grader/', include('grader.urls')),
    path('chat/', include('chatbot.urls')),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
