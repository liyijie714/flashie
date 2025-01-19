import os
import logging
import html
from django.conf import settings
from PyPDF2 import PdfReader
from gtts import gTTS
from datetime import datetime
import boto3
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file and escapes special SSML characters.
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
            extracted = page.extract_text()
            if extracted:
                # Escape special SSML characters
                extracted = html.escape(extracted)
                text += extracted + " "
            else:
                logger.warning(f"No text found on page {i+1}")
        
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

def format_text_to_ssml(text):
    """
    Converts plain text to SSML with enhanced formatting.
    """
    # Clean the text and escape special characters
    text = text.replace('&', '&amp;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    
    # Split into paragraphs
    paragraphs = text.split('\n\n')
    
    # Build SSML document
    ssml = '<speak>'
    
    for paragraph in paragraphs:
        if paragraph.strip():
            # Add pause between paragraphs
            ssml += f'<p>{paragraph.strip()}</p><break time="1s"/>'
    
    ssml += '</speak>'
    return ssml

def convert_text_to_speech_polly(text, output_filename, voice_id='Joanna', speech_rate='medium'):
    """
    Converts text to speech using Amazon Polly with basic SSML support.
    """
    try:
        # Initialize Polly client
        polly_client = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME
        ).client('polly')
        
        # Create audio directory
        audio_dir = os.path.join(settings.MEDIA_ROOT, 'audios')
        os.makedirs(audio_dir, exist_ok=True)
        
        # Basic SSML with <prosody>
        ssml_text = f'<speak><prosody rate="{speech_rate}">{text}</prosody></speak>'
        
        logger.info(f"Generated SSML: {ssml_text}")
        
        # Make the API call to Polly
        try:
            response = polly_client.synthesize_speech(
                Text=ssml_text,
                TextType='ssml',
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine='neural'
            )
            
            logger.info("Successfully received response from Polly")
            
            # Save the audio file
            if "AudioStream" in response:
                audio_path = os.path.join(audio_dir, output_filename)
                logger.info(f"Saving audio to: {audio_path}")
                
                with open(audio_path, 'wb') as file:
                    file.write(response['AudioStream'].read())
                
                logger.info("Audio file saved successfully")
                return f"audios/{output_filename}"
            else:
                logger.error("No AudioStream in response")
                raise Exception("No AudioStream in response")
                
        except ClientError as e:
            logger.error(f"Polly API error: {str(e)}")
            raise Exception(f"Polly API error: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error in convert_text_to_speech_polly: {str(e)}")
        raise Exception(f"Failed to generate audio: {str(e)}")

def format_text_to_speech_ssml(text):
    """
    Formats text with advanced SSML features for better speech synthesis.
    """
    ssml = '<speak>'
    
    # Split into sentences (basic implementation)
    sentences = text.split('. ')
    
    for sentence in sentences:
        # Clean the sentence
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Detect and handle numbers
        sentence = handle_numbers(sentence)
        
        # Add emphasis to important phrases (basic implementation)
        sentence = add_emphasis(sentence)
        
        # Add appropriate breaks and prosody
        ssml += f'<s><prosody rate="95%">{sentence}</prosody></s><break time="500ms"/>'
    
    ssml += '</speak>'
    return ssml

def handle_numbers(text):
    """
    Format numbers for better pronunciation.
    """
    import re
    
    # Handle dates
    text = re.sub(r'(\d{4})-(\d{2})-(\d{2})', 
                  lambda m: f'<say-as interpret-as="date" format="ymd">{m.group(0)}</say-as>', 
                  text)
    
    # Handle phone numbers
    text = re.sub(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})',
                  lambda m: f'<say-as interpret-as="telephone">{m.group(0)}</say-as>',
                  text)
    
    # Handle cardinal numbers
    text = re.sub(r'\b\d+\b',
                  lambda m: f'<say-as interpret-as="cardinal">{m.group(0)}</say-as>',
                  text)
    
    return text

def add_emphasis(text):
    """
    Add emphasis to important phrases.
    """
    # List of phrases that might need emphasis
    emphasis_phrases = [
        'important',
        'warning',
        'note',
        'caution',
        'danger'
    ]
    
    for phrase in emphasis_phrases:
        text = text.replace(
            f' {phrase} ',
            f' <emphasis level="strong">{phrase}</emphasis> '
        )
    
    return text

def get_available_voices():
    """
    Returns a list of available Polly voices.
    """
    try:
        polly_client = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME
        ).client('polly')
        
        response = polly_client.describe_voices(
            Engine='neural',
            LanguageCode='en-US'
        )
        
        return response['Voices']
        
    except (ClientError, BotoCoreError) as aws_error:
        logger.error(f"AWS Polly error while fetching voices: {str(aws_error)}")
        raise Exception(f"Error fetching voices: {str(aws_error)}")
    except Exception as e:
        logger.error(f"Error fetching voices: {str(e)}")
        raise Exception(f"Error fetching voices: {str(e)}") 