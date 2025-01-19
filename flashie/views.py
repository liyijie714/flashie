from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Document, UploadedPDF
from .forms import PDFUploadForm
from .utils import extract_text_from_pdf, convert_text_to_speech
import youtube_dl  # You'll need to install this package
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages 

def home(request):
    return render(request, 'flashie/home.html')

@login_required
def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = form.cleaned_data['pdf']
            uploaded_pdf = UploadedPDF.objects.create(user=request.user, pdf=pdf_file)
            uploaded_pdf.save()
            
            # Extract text from the uploaded PDF
            pdf_path = uploaded_pdf.pdf.path
            try:
                text = extract_text_from_pdf(pdf_path)
                if not text.strip():
                    messages.error(request, 'The uploaded PDF does not contain extractable text.')
                    uploaded_pdf.delete()
                    return redirect('flashie:upload_pdf')
            except Exception as e:
                messages.error(request, f'Error extracting text from PDF: {e}')
                uploaded_pdf.delete()
                return redirect('flashie:upload_pdf')
            
            # Convert extracted text to speech
            audio_filename = f"{uploaded_pdf.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.mp3"
            try:
                audio_relative_path = convert_text_to_speech(text, audio_filename)
                uploaded_pdf.audio = audio_relative_path
                uploaded_pdf.audio_generated_at = timezone.now()
                uploaded_pdf.save()
                messages.success(request, 'PDF uploaded and audio generated successfully.')
                return redirect('flashie:upload_pdf')
            except Exception as e:
                messages.error(request, f'Error generating audio: {e}')
                uploaded_pdf.delete()
                return redirect('flashie:upload_pdf')
        else:
            messages.error(request, 'Invalid form submission. Please upload a valid PDF file.')
    else:
        form = PDFUploadForm()
    
    user_pdfs = UploadedPDF.objects.filter(user=request.user).order_by('-uploaded_at')
    
    context = {
        'form': form,
        'user_pdfs': user_pdfs
    }
    
    return render(request, 'flashie/upload_pdf.html', context)

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