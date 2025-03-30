from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import os
from django.core.exceptions import ValidationError
import docx
from PyPDF2 import PdfReader
import logging
import fitz  # PyMuPDF for better PDF text extraction

logger = logging.getLogger(__name__)

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
    voice_id = models.CharField(max_length=50, default='Joanna')

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

class LectureSlide(models.Model):
    lecture = models.ForeignKey('Lecture', on_delete=models.CASCADE, related_name='slides')
    slide_number = models.IntegerField()
    title = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    annotation = models.TextField(blank=True)

    class Meta:
        ordering = ['slide_number']

    def generate_annotation(self):
        """Generate a concise annotation from the notes"""
        if not self.notes:
            return ""
            
        # Split into sentences and get key points
        sentences = [s.strip() for s in self.notes.split('.') if s.strip()]
        
        if not sentences:
            return ""
            
        # Take first sentence and limit to reasonable length
        main_point = sentences[0]
        if len(main_point) > 150:
            main_point = main_point[:147] + "..."
            
        return main_point

class Lecture(models.Model):
    title = models.CharField(max_length=200)
    presentation = models.FileField(
        upload_to='lectures/presentations/',
        help_text='Accepted formats: PDF, PPT, PPTX'
    )
    script = models.FileField(
        upload_to='lectures/scripts/',
        help_text='Accepted formats: PDF, TXT, DOC, DOCX'
    )
    processed_script = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def clean(self):
        if self.presentation:
            ext = self.presentation.name.split('.')[-1].lower()
            if ext not in ['pdf', 'ppt', 'pptx']:
                raise ValidationError('Presentation must be a PDF, PPT, or PPTX file.')
        if self.script:
            ext = self.script.name.split('.')[-1].lower()
            if ext not in ['pdf', 'txt', 'doc', 'docx']:
                raise ValidationError('Script must be a PDF, TXT, DOC, or DOCX file.')

    def process_script(self):
        """Process script and map to slides with annotations"""
        if not self.script or not self.presentation:
            return

        try:
            # First extract titles from PDF
            pdf_doc = fitz.open(self.presentation.path)
            slide_titles = []
            
            for page in pdf_doc:
                text = page.get_text()
                # Get first non-empty line as title
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                title = lines[0] if lines else f"Slide {len(slide_titles) + 1}"
                slide_titles.append(title)
            
            # Process script content
            content = self.script.read().decode('utf-8')
            slide_sections = content.split('\n\nSlide ')
            
            # Clear existing slides
            self.slides.all().delete()
            
            for i, section in enumerate(slide_sections, 1):
                if section.strip():
                    slide = LectureSlide.objects.create(
                        lecture=self,
                        slide_number=i,
                        title=slide_titles[i-1] if i <= len(slide_titles) else f"Slide {i}",
                        notes=section.strip()
                    )
                    
                    slide.annotation = slide.generate_annotation()
                    slide.save()
                    
        except Exception as e:
            logger.error(f"Error processing script: {str(e)}")
            raise 