from django.db import models
from django.contrib.auth.models import User

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
    pdf = models.FileField(upload_to='pdfs/')
    audio = models.FileField(upload_to='audios/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    audio_generated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.pdf.name}" 