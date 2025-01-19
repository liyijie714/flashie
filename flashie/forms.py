from django import forms
import boto3
from django.conf import settings

class PDFUploadForm(forms.Form):
    SPEECH_RATES = [
        ('x-slow', 'Very Slow'),
        ('slow', 'Slow'),
        ('medium', 'Medium'),
        ('fast', 'Fast'),
        ('x-fast', 'Very Fast'),
    ]
    
    pdf_file = forms.FileField(
        label='Select a PDF file',
        help_text='Maximum file size: 10MB',
        widget=forms.ClearableFileInput(attrs={
            'accept': 'application/pdf',
            'class': 'form-control',
            'required': True,
            'name': 'pdf_file'
        })
    )
    
    voice = forms.ChoiceField(
        label='Select Voice',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    speech_rate = forms.ChoiceField(
        label='Speech Rate',
        choices=SPEECH_RATES,
        initial='medium',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get available voices from Amazon Polly
        try:
            polly_client = boto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION_NAME
            ).client('polly')
            
            voices = polly_client.describe_voices(
                Engine='neural',
                LanguageCode='en-US'
            )['Voices']
            
            self.fields['voice'].choices = [
                (voice['Id'], f"{voice['Name']} ({voice['Gender']})") 
                for voice in voices
            ]
        except Exception:
            # Fallback to default voice if AWS call fails
            self.fields['voice'].choices = [('Joanna', 'Joanna (Female)')]

    def clean_pdf_file(self):
        pdf = self.cleaned_data.get('pdf_file')
        if not pdf:
            raise forms.ValidationError('Please select a PDF file.')
        
        if not pdf.name.endswith('.pdf'):
            raise forms.ValidationError('File must be a PDF.')
        
        if pdf.size > 10 * 1024 * 1024:  # 10MB
            raise forms.ValidationError('File size must be under 10MB.')
        
        return pdf 