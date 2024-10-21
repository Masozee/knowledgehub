import os
from decouple import config, Csv
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    #generated apps
    'app.api',
    'app.assets',
    'app.events',
    'app.people',
    'app.publications',
    'app.tools',
    'app.config',
    'app.project',
    'app.finance',

    #third party apps
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

LOGIN_REDIRECT_URL = 'web:index'  # Redirect to dashboard after login
LOGOUT_REDIRECT_URL = 'web:index'  # Redirect to dashboard after logout

# If you want to use custom templates, uncomment and modify these lines:
LOGIN_URL = 'login'
# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    },
    'logs_db': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'logs.sqlite3',
    },
    'analytics': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'analytics.sqlite3',
    }
}

DATABASE_ROUTERS = [
    'core.routers.DefaultRouter',
    'core.routers.LogsRouter',
    'core.routers.AnalyticsRouter'
]
        # Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = True


# CUSTOM USER CONFIG
AUTH_USER_MODEL = 'people.CustomUser'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]  # Directory where static files are stored during development
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (user uploads)
MEDIA_URL = '/media/'  # URL to access media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#Third Party Configuration
SITE_ID = 1

# Microsoft OAuth settings
AUTHENTICATION_BACKENDS = [
    'microsoft_auth.backends.MicrosoftAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend'
]

MICROSOFT_AUTH_CLIENT_ID = config('MICROSOFT_AUTH_CLIENT_ID')
MICROSOFT_AUTH_CLIENT_SECRET = config('MICROSOFT_AUTH_CLIENT_SECRET')
MICROSOFT_AUTH_LOGIN_TYPE = 'ma'  # Microsoft Account login

# Use Office 365 Authentication
MICROSOFT_AUTH_TENANT_ID = 'organizations'

MICROSOFT_AUTH_BASE_URL = 'https://login.microsoftonline.com'

# Update the redirect URI to use HTTPS
MICROSOFT_AUTH_REDIRECT_URI = 'https://localhost:8000/microsoft/auth-callback/'

# For extra security, you can set this to True in development
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


#LOGS Configurations
#LOG_FILE = os.path.join(BASE_DIR, 'django_logs.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'db_log': {
            'level': 'DEBUG',
            'class': 'core.logging.SQLiteLogHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['db_log'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Ensure the app directory is in the Python path
import sys
sys.path.append(str(BASE_DIR))

# Specify the login redirect URL
LOGIN_REDIRECT_URL = '/dashboard/'

AI_SERVICES = {
    'openai': {
        'api_key': config('OPENAI_API_KEY'),
        'model': 'gpt-3.5-turbo',  # or 'gpt-4' if you have access
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
        'model': 'llama-3.1-sonar-small-128k-online',
        'max_tokens': 1000,
    },
}

# OpenAI specific settings (if needed separately)
OPENAI_API_KEY = AI_SERVICES['openai']['api_key']

customColorPalette = [
        {
            'color': 'hsl(4, 90%, 58%)',
            'label': 'Red'
        },
        {
            'color': 'hsl(340, 82%, 52%)',
            'label': 'Pink'
        },
        {
            'color': 'hsl(291, 64%, 42%)',
            'label': 'Purple'
        },
        {
            'color': 'hsl(262, 52%, 47%)',
            'label': 'Deep Purple'
        },
        {
            'color': 'hsl(231, 48%, 48%)',
            'label': 'Indigo'
        },
        {
            'color': 'hsl(207, 90%, 54%)',
            'label': 'Blue'
        },
    ]

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],

    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
        'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable',],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}