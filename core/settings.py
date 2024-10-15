import os
from decouple import config

# Determine the environment
ENVIRONMENT = config('ENV', default='development')

# Set the appropriate settings module based on the environment
if ENVIRONMENT == 'production':
    settings_module = 'core.settings.production'
else:
    settings_module = 'core.settings.development'

# Import the selected settings
settings = __import__(settings_module, fromlist=[''])

# Now you can access all settings as attributes of `settings`
# For example: 
# DEBUG = settings.DEBUG
# DATABASES = settings.DATABASES
