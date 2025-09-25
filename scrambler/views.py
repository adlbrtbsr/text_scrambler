from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from .forms import UploadForm
from .utils import scramble_text
import unicodedata


def upload_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            f = form.cleaned_data['file']
            data = f.read()

            try:
                text = data.decode('utf-8-sig')
            except Exception:
                text = data.decode('utf-8', errors='replace')

            text = unicodedata.normalize('NFC', text)
            result = scramble_text(text)
            request.session['scrambled_text'] = result

            return redirect('result')
    else:
        form = UploadForm()

    return render(request, 'upload.html', {'form': form})


def result_view(request: HttpRequest) -> HttpResponse:
    result = request.session.get('scrambled_text')

    if not result:
        messages.info(request, 'No result to display. Please upload a text file.')
        return redirect('upload')

    return render(request, 'result.html', {'scrambled_text': result})
