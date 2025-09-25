## Text Scrambler Django App — Implementation Plan

This document outlines the end-to-end plan to implement a Django web app that scrambles words in an uploaded text file by shuffling interior letters while preserving the first and last letters.

### Goals
- Upload a `.txt` file from the main page.
- Read file server-side; scramble words by shuffling internal letters only.
- Preserve first and last letters of each word; keep punctuation and whitespace unchanged.
- Redirect to a result page that displays the scrambled output (no download endpoint).

---

### Architecture Overview
- **Framework**: Django (4.x or 5.x)
- **App name**: `scrambler`
- **Persistence**: Session storage only, used to carry scrambled text from POST to the result view (PRG pattern). No database models required.
- **Templates**: `base.html`, `upload.html`, `result.html`
- **URLs**:
  - `/` → GET upload form; POST handles file upload and processing, then redirects
  - `/result/` → GET display scrambled text (reads from session)
- **Validation**: Restrict to `text/plain`, set max upload size (e.g., 1 MB), UTF-8 decoding with fallback.

---

### Project Setup
1. Create project and app
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install "Django>=4.2,<6.0"
   django-admin startproject config .
   python manage.py startapp scrambler
   ```
2. Add `scrambler` to `INSTALLED_APPS` in `config/settings.py`.
3. Configure templates and static settings:
   - `TEMPLATES[0]['DIRS'] = [BASE_DIR / 'templates']`
   - `STATIC_URL = 'static/'`, `STATICFILES_DIRS = [BASE_DIR / 'static']`
4. Create directories: `templates/`, `static/`.

---

### URL Routing
- `config/urls.py`: include `scrambler.urls` at root.
- `scrambler/urls.py`:
  - `/` → `upload_view`
  - `/result/` → `result_view`

---

### Forms
- `scrambler/forms.py`:
  - `class UploadForm(forms.Form)` with `file = forms.FileField(...)`.
  - Server-side validation:
    - Content type check: `text/plain` (from `UploadedFile.content_type` if available)
    - Size limit (e.g., 1 MB) via `clean_file` and/or settings.

---

### Views and Flow
- `upload_view(request)`
  - GET: render `upload.html` with `UploadForm`.
  - POST:
    - Validate form and file constraints.
    - Read uploaded file bytes from `request.FILES['file']`.
    - Decode with `utf-8` (fallback to `latin-1` or use `errors='replace'`).
    - Process text via `scramble_text(text)`.
    - Store scrambled text in session (e.g., `request.session['scrambled_text'] = result`).
    - Redirect (`HttpResponseRedirect`) to `/result/`.
- `result_view(request)`
  - Read `scrambled_text` from session.
  - If missing, redirect back to `/` with a message.
  - Optionally clear the session key after read to avoid stale data.
  - Render `result.html` showing the result and actions (upload another).

---

### Scrambling Logic
- Module: `scrambler/utils.py`.
- Functions:
  - `scramble_word(word: str, rng: random.Random) -> str`
    - If `len(word) < 4`, return as-is (no interior to shuffle usefully).
    - Preserve first and last characters.
    - Shuffle interior letters using `rng.shuffle(list(...))`.
    - Ensure at least one change when possible; attempt limited retries (e.g., 5 attempts) to avoid infinite loops on repeated letters.
  - `scramble_text(text: str, rng: Optional[random.Random] = None) -> str`
    - Tokenize while preserving non-word tokens (whitespace, punctuation).
    - Suggested tokenization approach:
      - Use regex to capture sequences of letters for words and everything else as separators.
      - For English-only: `[A-Za-z]+`; for broader Unicode support consider `\p{L}+` via the `regex` package (optional dependency).
    - Apply `scramble_word` only to tokens classified as words.
- Punctuation, whitespace, and numbers remain unchanged.
- Hyphenated words: treat each segment as a separate word or keep as-is for MVP. Document behavior.

---

### Templates
- `templates/base.html`:
  - Basic layout, navbar/title, container.
  - Block for messages (Django messages framework) to show errors.
- `templates/upload.html`:
  - Upload form with CSRF token, file input, and submit button.
  - Display constraints (only `.txt`, max size).
- `templates/result.html`:
  - Preformatted block/textarea showing scrambled text from session.
  - Button/link to go back to upload.

---

### Settings & Security
- Enforce max upload size (e.g., `MAX_UPLOAD_SIZE=1_000_000`) in settings; validate in form.
- Restrict to text files: `text/plain` MIME and `.txt` extension hint (client-side accept attribute optional; server-side decisive).
- Session storage is default Django session backend (server-side or signed cookies depending on config). Consider clearing `scrambled_text` after display.
- Standard Django security hardening for production (`ALLOWED_HOSTS`, HTTPS, CSRF, secure cookies).

---

### Testing Strategy
- Unit tests (`scrambler/tests/test_utils.py`):
  - `scramble_word` preserves first/last letters.
  - Words < 4 unchanged.
  - Punctuation/whitespace preserved.
  - Deterministic results by injecting seeded `random.Random(42)`.
- Integration tests (`scrambler/tests/test_views.py`):
  - Upload flow: POST a text file to `/` returns 302 to `/result/`.
  - GET `/result/` renders the scrambled text in response.
  - Missing session content redirects to `/`.
- Edge cases:
  - Empty file.
  - Very long line.
  - File with non-ASCII characters (if supported).

---

### Developer Experience
- `requirements.txt`:
  - `Django>=4.2,<6.0`
  - Optional: `regex` for Unicode-aware word detection
- `Makefile` or simple scripts (optional): `make run`, `make test`, `make lint`.
- Pre-commit hooks (optional): basic formatting/linting.

---

### Deployment (Optional, Post-MVP)
- Environment variables via `.env` (SECRET_KEY, DEBUG, ALLOWED_HOSTS).
- Simple Dockerfile and `docker-compose.yml` for local/prod parity.
- Static files served via `whitenoise` or web server.

---

### Implementation Steps & Milestones
1. Scaffold project and app; configure settings and templates.
2. Create `UploadForm`; implement `upload_view` with validation and session storage.
3. Implement `scramble_word` and `scramble_text` in `utils.py` with tests.
4. Implement `result_view`; wire URLs for `/` and `/result/` with PRG flow.
5. Build templates: `base.html`, `upload.html`, `result.html`.
6. Add messages, error handling, and size/type limits.
7. Polish UI (basic CSS).
8. Add additional tests; finalize docs and README.

---

### Open Decisions (Document and Revisit)
- Unicode handling: restrict to `[A-Za-z]` vs. add `regex` for `\p{L}`.
- Hyphenated/compound words: split vs. treat entire token as non-scramble.
- Maximum file size and processing limits for MVP.

---

### Example Commands
```bash
# Run server
python manage.py migrate
python manage.py runserver

# Run tests
python manage.py test -v 2
```

---

### Acceptance Criteria
- Uploading a valid `.txt` file redirects to `/result/` where the scrambled text is displayed.
- First and last letter of each recognized word are preserved; punctuation/whitespace unchanged.
- Words shorter than 4 characters remain unchanged.
- Invalid uploads show clear form errors; empty upload yields a friendly message.
