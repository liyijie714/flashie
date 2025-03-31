import os
import logging
import html
from django.conf import settings
from PyPDF2 import PdfReader
from gtts import gTTS
from datetime import datetime
import boto3
import re
from botocore.exceptions import ClientError, BotoCoreError
from pdf2image import convert_from_path
import pytesseract
import nltk
from nltk.tokenize import sent_tokenize

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.
    Attempts to use pdfminer.six first. If extraction fails or text is empty, uses OCR.
    """
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(pdf_path)
        logger.info(f"********** Extracted text: {text}")
        if text.strip():
            return text.strip()
        else:
            logger.info("No text extracted using pdfminer.six. Attempting OCR.")
    except ImportError:
        logger.error("pdfminer.six is not installed.")
        raise

    # If pdfminer failed or text is empty, use OCR
    try:
        images = convert_from_path(pdf_path)
        ocr_text = ""
        for image in images:
            page_text = pytesseract.image_to_string(image)
            ocr_text += page_text + "\n"
        return ocr_text.strip()
    except Exception as e:
        logger.error(f"Error during OCR text extraction: {str(e)}")
        raise Exception(f"Failed to extract text from PDF using OCR: {str(e)}")

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
    Convert plain text into SSML with paragraphs, sentences, and breaks
    for a more natural read by Amazon Polly.
    """
    # Replace common special characters
    text = text.replace('&', '&amp;') \
               .replace('"', '&quot;') \
               .replace("'", '&apos;') \
               .replace('<', '&lt;') \
               .replace('>', '&gt;')

    # Handle numbers (dates, phone, cardinal)
    text = handle_numbers(text)

    # Optional: Add emphasis to certain words
    text = add_emphasis(text)

    # Split text into paragraphs
    paragraphs = text.split('\n\n')
    
    # Build the SSML
    ssml_parts = ['<speak>']
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # Split paragraph into sentences by period or other punctuation
        sentences = re.split(r'(?<=[.?!])\s+', paragraph)
        
        # Wrap each sentence in <s> tags, plus a slight pause
        paragraph_ssml = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                paragraph_ssml.append(
                    f'<s><prosody rate="95%">{sentence}</prosody></s>'
                )
        
        # Join sentences with a small break
        # Add an extra break after finishing the paragraph
        paragraph_str = '<break time="500ms"/>'.join(paragraph_ssml)
        paragraph_str += '<break time="1s"/>'
        ssml_parts.append(paragraph_str)
    
    ssml_parts.append('</speak>')
    return ''.join(ssml_parts)

def convert_text_to_speech_polly(text, output_filename, voice_id='Matthew', speech_rate='medium'):
    """
    Converts text to speech using Amazon Polly with a podcast style.
    Handles engine compatibility for different voices.
    """
    try:
        # Initialize Polly client
        polly_client = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME
        ).client('polly')

        # Create audio directory if it doesn't exist
        audio_dir = os.path.join(settings.MEDIA_ROOT, 'audios')
        os.makedirs(audio_dir, exist_ok=True)

        # Process text for more natural speech with better sentence detection
        processed_text = regex_based_text_processing_minimal(text)
        
        # Simplified SSML with only widely supported features
        ssml_text = f"""<speak>
            <prosody rate="{speech_rate}">
                {processed_text}
            </prosody>
        </speak>"""

        logger.info(f"Generated SSML: {ssml_text}")

        # First try neural engine as it sounds better
        try:
            response = polly_client.synthesize_speech(
                Text=ssml_text,
                TextType='ssml',
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine='neural'
            )
        except ClientError as e:
            if "ValidationException" in str(e) and "SSML features" in str(e):
                # If neural with SSML fails, try with plain text
                logger.info("Neural engine with SSML failed, trying neural with plain text...")
                response = polly_client.synthesize_speech(
                    Text=text,
                    OutputFormat='mp3',
                    VoiceId=voice_id,
                    Engine='neural'
                )
            else:
                # If other error with neural, try standard engine
                logger.info(f"Neural engine failed with error: {str(e)}, trying standard engine...")
                # List of voices that work with standard engine
                standard_compatible_voices = ['Joanna', 'Matthew', 'Salli', 'Justin', 'Kevin']
                
                # If current voice doesn't support standard, use a fallback
                if "does not support the selected engine: standard" in str(e):
                    fallback_voice = 'Matthew'  # Default fallback
                    logger.info(f"Voice {voice_id} doesn't support standard engine, using {fallback_voice}")
                    voice_id = fallback_voice
                
                response = polly_client.synthesize_speech(
                    Text=ssml_text,
                    TextType='ssml',
                    OutputFormat='mp3',
                    VoiceId=voice_id,
                    Engine='standard'
                )

        if "AudioStream" in response:
            audio_path = os.path.join(audio_dir, output_filename)
            with open(audio_path, 'wb') as file:
                file.write(response['AudioStream'].read())
            logger.info(f"Audio file saved to {audio_path}")
            return f"audios/{output_filename}"
        else:
            logger.error("No AudioStream in Polly response")
            raise Exception("No AudioStream in Polly response")

    except ClientError as e:
        logger.error(f"Polly API error: {str(e)}")
        
        # Last resort - try with plain text and Matthew voice on standard engine
        try:
            logger.info("Trying with plain text and Matthew voice as last resort...")
            response = polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId='Matthew',
                Engine='standard'
            )
            
            if "AudioStream" in response:
                audio_path = os.path.join(audio_dir, output_filename)
                with open(audio_path, 'wb') as file:
                    file.write(response['AudioStream'].read())
                logger.info(f"Audio file saved with fallback method to {audio_path}")
                return f"audios/{output_filename}"
        except Exception as inner_e:
            logger.error(f"Fallback attempt failed: {str(inner_e)}")
        
        raise Exception(f"Polly API error: {str(e)}")

    except Exception as e:
        logger.error(f"Error in convert_text_to_speech_polly: {str(e)}")
        raise Exception(f"Failed to generate audio: {str(e)}")

def regex_based_text_processing(text):
    """
    Fallback function that uses regex for sentence splitting when NLTK is unavailable.
    """
    import re
    
    # Clean up text by normalizing whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Use regex for sentence detection
    # This pattern looks for end punctuation followed by space and capital letter
    pattern = r'([.!?][\'")\]]*)\s+(?=[A-Z]|$)'
    
    # Split text into sentences
    sentence_parts = []
    last_end = 0
    for match in re.finditer(pattern, text):
        end = match.end()
        sentence_parts.append(text[last_end:end])
        last_end = end
    
    # Add any remaining text
    if last_end < len(text):
        sentence_parts.append(text[last_end:])
    
    # Process each sentence
    processed_parts = []
    for i, sentence in enumerate(sentence_parts):
        # Add breathing pauses at commas, semicolons, colons, and dashes
        sentence = re.sub(r'(,|;|:|—|-)\s+', r'\1<break time="250ms"/> ', sentence)
        
        # Add longer pause between sentences
        processed_parts.append(f"{sentence}<break time='650ms'/>")
    
    # Combine the parts and escape HTML but preserve SSML tags
    processed_text = " ".join(processed_parts)
    
    # Simple regex to preserve SSML tags
    processed_text = re.sub(r'<break\s+time=[\'"](\d+)ms[\'"]/>', 
                            lambda m: f"___BREAK_{m.group(1)}___", 
                            processed_text)
    
    # Escape HTML
    processed_text = html.escape(processed_text)
    
    # Restore SSML tags
    processed_text = re.sub(r'___BREAK_(\d+)___', 
                           lambda m: f'<break time="{m.group(1)}ms"/>', 
                           processed_text)
    
    return processed_text

def regex_based_text_processing_minimal(text):
    """
    Minimal text processing with only simple break tags.
    """
    import re
    
    # Clean up text by normalizing whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Use regex for sentence detection
    # This pattern looks for end punctuation followed by space and capital letter
    pattern = r'([.!?][\'")\]]*)\s+(?=[A-Z]|$)'
    
    # Split text into sentences
    sentence_parts = []
    last_end = 0
    for match in re.finditer(pattern, text):
        end = match.end()
        sentence_parts.append(text[last_end:end])
        last_end = end
    
    # Add any remaining text
    if last_end < len(text):
        sentence_parts.append(text[last_end:])
    
    # Process each sentence - only add breaks between sentences
    processed_parts = []
    for sentence in sentence_parts:
        processed_parts.append(f"{html.escape(sentence)}<break time='500ms'/>")
    
    # Combine the parts
    return " ".join(processed_parts)

def insert_breaks_and_structure(text):
    # Escape any XML special characters
    escaped_text = html.escape(text)

    # Insert SSML <break> tags after sentence-ending punctuation
    escaped_text = re.sub(r'([.?!])', rf'\1<break time="{break_time_ms}"/>', escaped_text)

    # Wrap each paragraph or sentence group with <p> tags
    paragraphs = escaped_text.split('\n')
    structured_text = ''.join([f"<p>{para.strip()}</p>" for para in paragraphs if para.strip()])

    return structured_text

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
    Format numbers for better Polly pronunciation using SSML <say-as> tags.
    """
    # Dates: 2023-03-15 => read as date
    text = re.sub(
        r'(\d{4})-(\d{2})-(\d{2})',
        lambda m: f'<say-as interpret-as="date" format="ymd">{m.group(0)}</say-as>',
        text
    )
    # Phone numbers
    text = re.sub(
        r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})',
        lambda m: f'<say-as interpret-as="telephone">{m.group(0)}</say-as>',
        text
    )
    # Basic cardinal numbers
    text = re.sub(
        r'\b\d+\b',
        lambda m: f'<say-as interpret-as="cardinal">{m.group(0)}</say-as>',
        text
    )
    return text

def add_emphasis(text):
    """
    Add emphasis to certain keywords or phrases using <emphasis>.
    """
    emphasis_phrases = ['important', 'warning', 'note', 'caution', 'danger']
    for phrase in emphasis_phrases:
        regex_pattern = r'\b' + re.escape(phrase) + r'\b'
        text = re.sub(
            regex_pattern,
            f'<emphasis level="strong">{phrase}</emphasis>',
            text,
            flags=re.IGNORECASE
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

# Download the necessary data (run once)
nltk.download('punkt') 