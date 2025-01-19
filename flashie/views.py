from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404
from .models import Document, UploadedPDF
from .forms import PDFUploadForm
from .utils import extract_text_from_pdf, convert_text_to_speech, convert_text_to_speech_polly
import youtube_dl  # You'll need to install this package
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages 
import os
import logging

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'flashie/home.html')

@login_required
def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        uploaded_pdf = None
        
        if form.is_valid():
            try:
                # Get form data
                pdf_file = form.cleaned_data['pdf_file']
                voice_id = form.cleaned_data['voice']
                speech_rate = form.cleaned_data['speech_rate']
                
                logger.info(f"Processing upload for file: {pdf_file.name}")
                logger.info(f"Selected voice: {voice_id}")
                logger.info(f"Selected speech rate: {speech_rate}")
                
                # Create the PDF record
                uploaded_pdf = UploadedPDF.objects.create(
                    user=request.user,
                    pdf=pdf_file,
                    voice_id=voice_id
                )
                logger.info(f"Created UploadedPDF record with ID: {uploaded_pdf.id}")
                
                # Extract text from PDF
                logger.info("Starting text extraction...")
                text = extract_text_from_pdf(uploaded_pdf.pdf.path)
                
                if not text:
                    raise Exception("No text could be extracted from the PDF")
                
                logger.info(f"Extracted {len(text)} characters of text")
                
                # Generate audio filename
                timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                audio_filename = f"audio_{uploaded_pdf.id}_{timestamp}.mp3"
                logger.info(f"Generated audio filename: {audio_filename}")
                
                # Convert text to speech using Polly
                logger.info("Starting text-to-speech conversion...")
                audio_relative_path = convert_text_to_speech_polly(
                    text=text,
                    output_filename=audio_filename,
                    voice_id=voice_id,
                    speech_rate=speech_rate
                )
                
                logger.info(f"Audio generated successfully at: {audio_relative_path}")
                
                # Update the UploadedPDF instance
                uploaded_pdf.audio = audio_relative_path
                uploaded_pdf.audio_generated_at = timezone.now()
                uploaded_pdf.save()
                
                logger.info("UploadedPDF record updated with audio information")
                
                messages.success(request, 'PDF uploaded and audio generated successfully!')
                return redirect('flashie:upload_pdf')
                
            except Exception as e:
                logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
                if uploaded_pdf:
                    logger.info(f"Cleaning up failed upload: {uploaded_pdf.id}")
                    uploaded_pdf.delete()
                messages.error(request, f"Error processing PDF: {str(e)}")
        else:
            logger.error(f"Form validation errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PDFUploadForm()
    
    user_pdfs = UploadedPDF.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'flashie/upload_pdf.html', {
        'form': form,
        'user_pdfs': user_pdfs
    })

@login_required
def extract_video_script(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_url')
        if not video_url:
            return JsonResponse({'error': 'No URL provided'}, status=400)
            
        try:
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitlesformat': 'srt',
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                # Extract and process subtitles/transcript
                # This is a placeholder - you'll need to implement the actual extraction logic
                
            return JsonResponse({'success': True, 'transcript': 'Transcript text here'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def serve_audio(request, pdf_id):
    try:
        pdf = UploadedPDF.objects.get(id=pdf_id, user=request.user)
        if pdf.audio and os.path.exists(pdf.audio.path):
            response = FileResponse(open(pdf.audio.path, 'rb'))
            response['Content-Type'] = 'audio/mpeg'
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf.audio.name)}"'
            return response
        raise Http404("Audio file not found")
    except UploadedPDF.DoesNotExist:
        raise Http404("PDF not found")

@login_required
def serve_pdf(request, pdf_id):
    try:
        pdf = UploadedPDF.objects.get(id=pdf_id, user=request.user)
        if pdf.pdf and os.path.exists(pdf.pdf.path):
            response = FileResponse(open(pdf.pdf.path, 'rb'))
            response['Content-Type'] = 'application/pdf'
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf.pdf.name)}"'
            return response
        raise Http404("PDF file not found")
    except UploadedPDF.DoesNotExist:
        raise Http404("PDF not found") 