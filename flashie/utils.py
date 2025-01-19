import os
from django.conf import settings
from PyPDF2 import PdfReader
from gtts import gTTS
from datetime import datetime

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.

    :param pdf_path: Path to the PDF file.
    :return: Extracted text as a string.
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + " "
    return text

def convert_text_to_speech(text, output_filename):
    """
    Converts text to speech and saves it as an MP3 file.

    :param text: Text to convert.
    :param output_filename: Filename for the output audio.
    :return: Path to the generated audio file.
    """
    tts = gTTS(text)
    audio_path = os.path.join(settings.MEDIA_ROOT, 'audios', output_filename)
    tts.save(audio_path)
    return f"audios/{output_filename}" 