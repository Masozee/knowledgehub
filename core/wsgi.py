"""
WSGI config for Knowledgehub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from decouple import config
from django.core.wsgi import get_wsgi_application

# Get environment from the .env file and set appropriate settings
env = config('ENV', default='development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'core.settings.{env}')

application = get_wsgi_application()
