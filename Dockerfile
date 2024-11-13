# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.6.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    DJANGO_SETTINGS_MODULE=core.settings.development

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
        git \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Add Poetry to PATH
ENV PATH="${POETRY_HOME}/bin:${PATH}"

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-root --no-interaction

# Copy project
COPY . .

# Create necessary directories and log file with proper permissions
RUN mkdir -p /app/staticfiles /app/mediafiles /app/logs \
    && touch /app/logs/django.log \
    && chmod -R 777 /app/logs \
    && chmod 666 /app/logs/django.log

# Collect static files
RUN python manage.py collectstatic --noinput || true