from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Document
import youtube_dl  # You'll need to install this package

@login_required
def home(request):
    return render(request, 'flashie/home.html')

@login_required
def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        # Add validation for PDF file type
        if not pdf_file.name.endswith('.pdf'):
            return JsonResponse({'error': 'File must be a PDF'}, status=400)
            
        document = Document.objects.create(
            user=request.user,
            file=pdf_file,
            title=pdf_file.name
        )
        return JsonResponse({'success': True, 'document_id': document.id})
    return JsonResponse({'error': 'No file provided'}, status=400)

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