from django import forms

class PDFUploadForm(forms.Form):
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

    def clean_pdf_file(self):
        pdf = self.cleaned_data.get('pdf_file')
        if not pdf:
            raise forms.ValidationError('Please select a PDF file.')
        
        if not pdf.name.endswith('.pdf'):
            raise forms.ValidationError('File must be a PDF.')
        
        if pdf.size > 10 * 1024 * 1024:  # 10MB
            raise forms.ValidationError('File size must be under 10MB.')
        
        return pdf 