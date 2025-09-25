## Text Scrambler — Django App

Scramble the interior letters of words in an uploaded `.txt` file while preserving the first and last letters, punctuation, and whitespace.

### Features
- **Upload** a `.txt` file from the main page
- **PRG flow**: POST → redirect → result page
- **Scrambling**: only interior letters of words are shuffled; words < 4 chars unchanged
- **Preserves** punctuation and whitespace
- **Limits**: MIME `text/plain`

### Tech Stack
- Django (4.x/5.x compatible)
- ASGI app (`config.asgi`); recommended: Gunicorn + Uvicorn worker
- Static files via WhiteNoise (manifest, compressed)
- SQLite by default; Postgres via `DATABASE_URL` (using `dj-database-url`)
- App: `scrambler`

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

### Containerized usage (Docker + Makefile)

```bash
# Build the image
make build

# Run the app (binds :8000, runs migrations, serves via Gunicorn+Uvicorn)
make run

# Override port
PORT=8080 make run

# Tail logs / stop the container
make logs
make stop

# Run tests inside the container
make test

# Open a shell in the running container
make shell
```

Environment variables honored by the container: `DJANGO_SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`.

- Default database is SQLite at `/app/db.sqlite3` inside the container. Override with `DATABASE_URL` for Postgres.
- Static files are collected during build; migrations run automatically on container start.

### Environment Setup

The app reads configuration from environment variables (see `config/settings.py`). For local development you can export them in your shell or use a `.env` loader of your choice.

Required/important variables:
- `DJANGO_SECRET_KEY`: a long random string. Use a dedicated value in production.
- `DEBUG`: `True` or `False` (default `True`). Set `False` in production.
- `ALLOWED_HOSTS`: comma-separated hostnames (e.g., `example.com,www.example.com`). Required when `DEBUG=False`.
 - `ALLOWED_HOSTS`: comma-separated hostnames (e.g., `example.com,www.example.com`). When `DEBUG=False`, defaults to `*` if unset (Docker/Makefile also default to `*`). Override with your real domains in production.
- `CSRF_TRUSTED_ORIGINS`: comma-separated origins (scheme + host), e.g., `https://example.com,https://www.example.com`.
- `DATABASE_URL`: database connection URL. Defaults to local SQLite if not set. Example for Postgres: `postgres://USER:PASS@HOST:5432/DBNAME`.
- `CONN_MAX_AGE`: persistent DB connections in seconds (default `60`).
- `DB_SSL_REQUIRE`: `True` to require SSL for DB connections.
- `SECURE_SSL_REDIRECT`: `True` to force HTTPS in production (default `True` when `DEBUG=False`). Ensure your proxy sets `X-Forwarded-Proto`.

Example `.env` (do not commit real secrets):
```bash
DJANGO_SECRET_KEY=change-me
DEBUG=False
ALLOWED_HOSTS=your.domain.com
CSRF_TRUSTED_ORIGINS=https://your.domain.com
DATABASE_URL=sqlite:///$(pwd)/db.sqlite3
CONN_MAX_AGE=60
DB_SSL_REQUIRE=False
SECURE_SSL_REDIRECT=True
```

### Production

Install dependencies, collect static files (served by WhiteNoise), run migrations, and start with an ASGI server:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Example: Gunicorn with Uvicorn worker
gunicorn -k uvicorn.workers.UvicornWorker config.asgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
```

Health check endpoint (for load balancers / orchestrators):
```text
GET /health  ->  {"status": "ok"}
```

### How It Works
- Upload handled in `scrambler/views.py` (`upload_view`)
- Text is read server-side, decoded as UTF‑8 (BOM-safe) with replacement on errors, then normalized to NFC
- Scrambling is performed by `scrambler/utils.py`:
  - `scramble_word(word, rng)`: preserves first/last letters, shuffles interior
  - `scramble_text(text, rng=None)`: scrambles only tokens matching `(?:\p{L}\p{M}*)+` (Unicode letters)
- Result is stored in session and shown by `result_view`

### Behavior & Constraints
- **Word detection**: `(?:\p{L}\p{M}*)+` (Unicode letters with combining marks)
  - Non-letter characters (digits, punctuation, symbols) are left unchanged
- **Hyphenated words**: each alphabetic segment between punctuation is scrambled separately; hyphens are preserved
- **Length rule**: words with fewer than 4 characters are left unchanged
- **Size limit**: `MAX_UPLOAD_SIZE = 1_000,000` bytes (set in `config/settings.py`)
  - To change the upload size limit, update `MAX_UPLOAD_SIZE` in `config/settings.py` (value is in bytes). Validation uses this setting in `scrambler/forms.py`.
- **MIME check**: rejects non-`text/plain` uploads when a content type is provided by the client

### Endpoints
- `/` (GET): upload form
- `/` (POST): handle upload, process, and redirect
- `/result/` (GET): show scrambled text from session
- `/health` (GET): JSON health check `{ "status": "ok" }`
- `/admin/` (GET): Django admin

### Project Structure (key files)
```
config/
  settings.py        # Django settings (env utils, security, static/WhiteNoise)
  urls.py            # Includes scrambler URLs at root (+ /health)
  asgi.py            # ASGI entrypoint
  wsgi.py            # WSGI entrypoint (legacy)
  env_utils.py       # get_str/get_bool/get_int/get_list helpers
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
# In Docker
make test

# Or locally
source .venv/bin/activate
python manage.py test -v 2
```
Tests live in `scrambler/tests/` and cover utilities and upload/result flow.

### Development Notes
- Requirements in `requirements.txt` (includes Django, `regex`, `whitenoise`, `dj-database-url`, `sentry-sdk`)
- Sentry SDK is present in dependencies but not configured by default; integrate if you need error monitoring
- Static files are served from `static/` in dev; in prod, collected to `staticfiles/` and served by WhiteNoise
- Recommended production run: ASGI via Gunicorn + Uvicorn worker
- No database models required for MVP (SQLite default; Postgres supported via `DATABASE_URL`)
