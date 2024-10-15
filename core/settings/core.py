import os
from pathlib import Path
from decouple import config

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Default settings for all environments
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Your apps
    'app.api',
    'app.assets',
    'app.events',
    'app.people',
    'app.publications',
    'app.tools',
    'app.config',
    'app.project',

    # Third-party apps
    'microsoft_auth',
    'django_extensions',
    'import_export',
    'django_ckeditor_5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'microsoft_auth.context_processors.microsoft',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
AUTHENTICATION_BACKENDS = [
    'microsoft_auth.backends.MicrosoftAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend'
]

AUTH_USER_MODEL = 'people.CustomUser'
LOGIN_REDIRECT_URL = 'web:index'
LOGOUT_REDIRECT_URL = 'web:index'

# Microsoft OAuth settings
MICROSOFT_AUTH_CLIENT_ID = config('MICROSOFT_AUTH_CLIENT_ID')
MICROSOFT_AUTH_CLIENT_SECRET = config('MICROSOFT_AUTH_CLIENT_SECRET')
MICROSOFT_AUTH_LOGIN_TYPE = 'ma'
MICROSOFT_AUTH_TENANT_ID = 'organizations'
MICROSOFT_AUTH_BASE_URL = 'https://login.microsoftonline.com'
MICROSOFT_AUTH_REDIRECT_URI = 'https://localhost:8000/microsoft/auth-callback/'

# Static and Media files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CKEditor settings
customColorPalette = [
    {'color': 'hsl(4, 90%, 58%)', 'label': 'Red'},
    {'color': 'hsl(340, 82%, 52%)', 'label': 'Pink'},
    {'color': 'hsl(291, 64%, 42%)', 'label': 'Purple'},
    {'color': 'hsl(262, 52%, 47%)', 'label': 'Deep Purple'},
    {'color': 'hsl(231, 48%, 48%)', 'label': 'Indigo'},
    {'color': 'hsl(207, 90%, 54%)', 'label': 'Blue'},
]
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload'],
    },
    'extends': {
        'blockToolbar': ['paragraph', 'heading1', 'heading2', 'heading3',
                         '|', 'bulletedList', 'numberedList', '|', 'blockQuote'],
        'toolbar': ['heading', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
                    'code', 'subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing',
                    'insertImage', 'bulletedList', 'numberedList', 'todoList', '|',
                    'blockQuote', 'imageUpload'],
    },
    'image': {
        'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                    'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side'],
    },
    'table': {
        'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells', 'tableProperties', 'tableCellProperties'],
        'tableProperties': {'borderColors': customColorPalette, 'backgroundColors': customColorPalette},
        'tableCellProperties': {'borderColors': customColorPalette, 'backgroundColors': customColorPalette},
    },
}

# AI Services configuration
AI_SERVICES = {
    'openai': {
        'api_key': config('OPENAI_API_KEY'),
        'model': 'gpt-3.5-turbo',
        'max_tokens': 1000,
        'temperature': 0.7,
    },
    'anthropic': {
        'api_key': config('ANTHROPIC_API_KEY'),
        'model': 'claude-3-5-sonnet-20240620',
        'max_tokens': 1024,
    },
    'perplexity': {
        'api_key': config('PERPLEXITY_API_KEY'),
        'model': 'mixtral-8x7b-instruct',
        'max_tokens': 1000,
    },
}
