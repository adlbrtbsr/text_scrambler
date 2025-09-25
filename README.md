## Text Scrambler — Django App

Scramble the interior letters of words in an uploaded `.txt` file while preserving the first and last letters, punctuation, and whitespace.

### Features
- **Upload** a `.txt` file from the main page
- **PRG flow**: POST → redirect → result page
- **Scrambling**: only interior letters of words are shuffled; words < 4 chars unchanged
- **Preserves** punctuation and whitespace
- **Limits**: MIME `text/plain`, max size 1 MB

### Tech Stack
- Django (4.x/5.x compatible)
- App: `scrambler`
- Session storage only (no database models)

### Quickstart
```bash
# Enter the project directory
cd text_scrambler

# Create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and start the server
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` and upload a `.txt` file.

### How It Works
- Upload handled in `scrambler/views.py` (`upload_view`)
- Text is read server-side, decoded as UTF‑8 (with replacement on errors)
- Scrambling is performed by `scrambler/utils.py`:
  - `scramble_word(word, rng)`: preserves first/last letters, shuffles interior
  - `scramble_text(text, rng=None)`: scrambles only tokens matching `[A-Za-z]+`
- Result is stored in session and shown by `result_view`

### Behavior & Constraints
- **Word detection**: `[A-Za-z]+` (English letters only)
  - Non-ASCII letters and numbers are left unchanged
- **Hyphenated words**: each alphabetic segment between punctuation is scrambled separately; hyphens are preserved
- **Length rule**: words with fewer than 4 characters are left unchanged
- **Size limit**: `MAX_UPLOAD_SIZE = 1_000_000` bytes (set in `config/settings.py`)
- **MIME check**: rejects non-`text/plain` uploads when a content type is provided by the client

### Endpoints
- `/` (GET): upload form
- `/` (POST): handle upload, process, and redirect
- `/result/` (GET): show scrambled text from session

### Project Structure (key files)
```
config/
  settings.py        # Django settings (templates/static dirs, MAX_UPLOAD_SIZE)
  urls.py            # Includes scrambler URLs at root
scrambler/
  forms.py           # Upload form + validation (MIME, size)
  utils.py           # scramble_word / scramble_text
  views.py           # upload_view / result_view (PRG)
  urls.py            # route: '/' and '/result/'
templates/
  base.html          # layout, messages
  upload.html        # upload form
  result.html        # result display
```

### Testing
```bash
source .venv/bin/activate
python manage.py test -v 2
```
Tests live in `scrambler/tests/` and cover utilities and upload/result flow.

### Development Notes
- Requirements in `requirements.txt` (Django and `regex` dependency already present)
- Static files served from `static/` (during development)
- No database models required for MVP

### Future Enhancements (Optional)
- Unicode-aware word detection via the `regex` package using `\p{L}+`
- Configurable maximum file size and MIME validation
- Download endpoint for processed text
- Dockerfile and production hardening


