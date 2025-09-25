# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH="/app"

WORKDIR /app

# System deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps first (leverage layer caching)
COPY requirements.txt ./
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir gunicorn uvicorn

# Copy project
COPY . .

# Create a non-root user
RUN useradd --create-home appuser \
 && chown -R appuser:appuser /app
USER appuser

# Collect static at build time (safe even if DEBUG=True)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Default envs for convenience (override in runtime)
ENV PORT=8000 \
    DJANGO_SETTINGS_MODULE=config.settings \
    SECRET_KEY=dev-insecure-key \
    DEBUG=True \
    ALLOWED_HOSTS=*

# Run migrations on container start, then start ASGI via Gunicorn+Uvicorn
CMD sh -c "python manage.py migrate --noinput && gunicorn -k uvicorn.workers.UvicornWorker config.asgi:application --bind 0.0.0.0:${PORT} --workers ${GUNICORN_WORKERS:-3} --timeout ${GUNICORN_TIMEOUT:-60}"


