from django.contrib import admin
from .models import UploadedPDF

@admin.register(UploadedPDF)
class UploadedPDFAdmin(admin.ModelAdmin):
    list_display = ['user', 'pdf', 'audio', 'uploaded_at', 'audio_generated_at']
    search_fields = ['user__username', 'pdf'] 