import os
from decouple import config
from pathlib import Path
import ssl
import certifi

REQUESTS_VERIFY = certifi.where()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Core Settings
DEBUG = True
ENV = config('ENV', default='production')
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'tools.csis.or.id']
ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'
SITE_ID = 1

# Application definition
DJANGO_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

PROJECT_APPS = [
    'app.api',
    'app.assets',
    'app.events',
    'app.people',
    'app.publications',
    'app.tools',
    'app.config',
    'app.project',
    'app.finance',
    'app.web',
]

THIRD_PARTY_APPS = [
    'django_extensions',
    'import_export',
    'django_ckeditor_5',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.microsoft',
    'formtools',
    'model_utils',
    'crispy_forms',
    'crispy_bootstrap5',
    'taggit',
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'core.middleware.CurrentUserMiddleware'
]

# Authentication Settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Template Settings
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
            ],
        },
    },
]

# Database Settings
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

# Authentication and User Settings
AUTH_USER_MODEL = 'people.CustomUser'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# Authentication URLs and Settings
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/logout/'

# AllAuth Settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'

# Social Authentication Settings
SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional'  # Since you want email verification
SOCIALACCOUNT_EMAIL_REQUIRED = True            # Email is required
SOCIALACCOUNT_AUTO_SIGNUP = True              # Automatic signup for better UX
SOCIALACCOUNT_LOGIN_ON_GET = True             # Smoother OAuth flow
SOCIALACCOUNT_QUERY_EMAIL = True              # Always get email from provider
SOCIALACCOUNT_STORE_TOKENS = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID'),
            'secret': config('GOOGLE_CLIENT_SECRET'),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
            'https://www.googleapis.com/auth/photoslibrary.readonly',  # Add this scope
            'https://www.googleapis.com/auth/photoslibrary',  # Add this scope
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',  # Changed to offline to get refresh token
            'prompt': 'consent'  # Add this to ensure we get refresh token
        }
    },
    'microsoft': {
        'APP': {
            'client_id': config('MICROSOFT_AUTH_CLIENT_ID'),
            'secret': config('MICROSOFT_AUTH_CLIENT_SECRET'),

        },
        'SCOPE': [
            'User.Read',
            'profile',
            'email',
            'openid'
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'METHOD': 'oauth2',
        'VERIFIED_EMAIL': True,
        'EXCHANGE_TOKEN': True,
        'TENANT': 'organizations',
    }
}

SOCIALACCOUNT_AUTO_SIGNUP = True

SOCIALACCOUNT_FORMS = {
    'signup': 'app.people.forms.SocialAccountSignupForm'
}

# Localization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True

# Static and Media Files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security Settings
# Add these settings
CSRF_TRUSTED_ORIGINS = ['https://tools.csis.or.id']
CSRF_USE_SESSIONS = True  # More secure than cookie-based CSRF
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Logging Configuration
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
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['db_log'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends.schema': {  # Add this to handle admin log issues
            'handlers': ['null'],
            'propagate': False,
        },

        'django.contrib.admin': {  # Add this to handle admin-specific logs
            'handlers': ['null'],
            'propagate': False,
        },

    },
}

# AI Services Configuration
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
        'model': 'llama-3.1-sonar-small-128k-online',
        'max_tokens': 1000,
    },
}

# CKEditor Configuration
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
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
                   'code', 'subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                   'bulletedList', 'numberedList', 'todoList', '|', 'blockQuote', 'imageUpload', '|',
                   'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                   'insertTable'],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                       'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side', '|'],
            'styles': ['full', 'side', 'alignLeft', 'alignRight', 'alignCenter'],
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                             'tableProperties', 'tableCellProperties'],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'}
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

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"