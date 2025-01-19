from django import forms

class PDFUploadForm(forms.Form):
    pdf = forms.FileField(
        label='Select a PDF file',
        help_text='Maximum size: 10MB',
        widget=forms.ClearableFileInput(attrs={'accept': 'application/pdf'})
    ) 