import os
import logging
from django.conf import settings
from PyPDF2 import PdfReader
from gtts import gTTS
from datetime import datetime

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.
    """
    logger.info(f"Starting text extraction from: {pdf_path}")
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at path: {pdf_path}")
            
        logger.info("Opening PDF file...")
        reader = PdfReader(pdf_path)
        logger.info(f"PDF opened successfully. Number of pages: {len(reader.pages)}")
        
        text = ""
        for i, page in enumerate(reader.pages):
            logger.info(f"Processing page {i+1}/{len(reader.pages)}")
            text += page.extract_text() + " "
        
        text = text.strip()
        logger.info(f"Text extraction complete. Extracted {len(text)} characters")
        return text
        
    except Exception as e:
        logger.error(f"Error in extract_text_from_pdf: {str(e)}", exc_info=True)
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def convert_text_to_speech(text, output_filename):
    """
    Converts text to speech and saves it as an MP3 file.
    """
    logger.info(f"Starting text-to-speech conversion for file: {output_filename}")
    try:
        # Create the audios directory if it doesn't exist
        audio_dir = os.path.join(settings.MEDIA_ROOT, 'audios')
        os.makedirs(audio_dir, exist_ok=True)
        logger.info(f"Audio directory ensured: {audio_dir}")
        
        # Generate the audio file
        logger.info("Initializing gTTS...")
        tts = gTTS(text=text, lang='en')
        
        # Create the full path for the audio file
        audio_path = os.path.join(audio_dir, output_filename)
        logger.info(f"Saving audio to: {audio_path}")
        
        # Save the audio file
        tts.save(audio_path)
        logger.info("Audio file saved successfully")
        
        # Return the relative path for database storage
        relative_path = f"audios/{output_filename}"
        logger.info(f"Returning relative path: {relative_path}")
        return relative_path
        
    except Exception as e:
        logger.error(f"Error in convert_text_to_speech: {str(e)}", exc_info=True)
        raise Exception(f"Error generating audio: {str(e)}") 