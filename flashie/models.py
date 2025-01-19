from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import os

def pdf_upload_path(instance, filename):
    # Upload PDFs to MEDIA_ROOT/pdfs/user_<id>/filename
    return f'pdfs/user_{instance.user.id}/{filename}'

def audio_upload_path(instance, filename):
    # Upload audio files to MEDIA_ROOT/audios/user_<id>/filename
    return f'audios/user_{instance.user.id}/{filename}'

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title 

class UploadedPDF(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_pdfs')
    pdf = models.FileField(upload_to=pdf_upload_path)
    audio = models.FileField(upload_to=audio_upload_path, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    audio_generated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {os.path.basename(self.pdf.name)}"

    @property
    def pdf_url(self):
        """Returns the URL for the PDF file"""
        if self.pdf:
            return self.pdf.url
        return None

    @property
    def audio_url(self):
        """Returns the URL for the audio file"""
        if self.audio:
            return self.audio.url
        return None

    def delete(self, *args, **kwargs):
        # Delete the physical files when the model instance is deleted
        if self.pdf:
            if os.path.isfile(self.pdf.path):
                os.remove(self.pdf.path)
        if self.audio:
            if os.path.isfile(self.audio.path):
                os.remove(self.audio.path)
        super().delete(*args, **kwargs) 