from django import forms
from django.conf import settings


class UploadForm(forms.Form):
    file = forms.FileField(allow_empty_file=True)

    def clean_file(self):
        uploaded = self.cleaned_data['file']
        content_type = getattr(uploaded, 'content_type', None)
        if content_type and content_type != 'text/plain':
            raise forms.ValidationError('Only plain text files are allowed (text/plain).')
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 1_000_000)
        if uploaded.size is not None and uploaded.size > max_size:
            raise forms.ValidationError('File too large. Maximum allowed size is 1 MB.')
        return uploaded


