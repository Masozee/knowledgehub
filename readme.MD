# Knowledgehub

Knowledgehub is a Django-based web application designed to manage and organize information across various domains.

## Features

- User Authentication (including Microsoft Authentication)
- Admin Interface
- Multiple Apps:
  - Web
  - Publications
  - People
  - Events
  - Assets
  - API
  - Config
  - Tools (including Analytics)
- Custom Management Commands
- Static and Media File Handling
- Visitor Analytics

## Project Structure

The project is organized into several Django apps:

- `app/web`: Main web interface
- `app/publications`: Manage publications
- `app/people`: Manage people-related information
- `app/events`: Handle event-related functionality
- `app/assets`: Manage digital assets
- `app/api`: API endpoints
- `app/config`: Configuration-related functionality
- `app/tools`: Custom management commands, utilities, and analytics

## Setup

1. Clone the repository
2. Create a virtual environment and activate it
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the databases:
   ```bash
   python manage.py migrate
   python manage.py migrate --database=analytics
   ```
5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
6. Download a GeoIP database (e.g., GeoLite2-Country.mmdb) and update the path in `app/tools/analytics.py`:
   ```python
   reader = geoip2.database.Reader('/path/to/GeoLite2-Country.mmdb')
   ```
7. Run the development server with HTTPS support:
   ```bash
   python manage.py runserver_plus --cert certs/localhost+2.pem --key certs/localhost+2-key.pem
   ```

   This command uses `runserver_plus` from Django Extensions to run the server with HTTPS support. Make sure you have the necessary certificate and key files in the `certs` directory.

## Configuration

The main settings file is located at `core/settings.py`. Make sure to configure the following:

- Database settings (including the analytics database)
- Static and media file settings
- Microsoft Authentication settings (if using)

## Analytics Feature

The analytics feature tracks visitor data and is integrated into the `app.tools` Django app.

### Analytics Capabilities

- Tracks visitor information including:
  - Source (referrer)
  - Device type
  - Browser
  - Operating System
  - Country (based on IP address)
  - IP address
- Uses a separate SQLite database for analytics data

### Using Analytics

To collect visitor data in a view:

```python
from app.tools.analytics import collect_visitor_data

def your_view(request):
    collect_visitor_data(request)
    # Rest of your view logic
    # ...
```

### Accessing Analytics Data

Query analytics data using Django's ORM:

```python
from app.tools.models import AnalyticsVisitorData

# Example: Get all visitor data
all_data = AnalyticsVisitorData.objects.using('analytics').all()

# Example: Get visitor count by country
from django.db.models import Count
country_stats = AnalyticsVisitorData.objects.using('analytics').values('country').annotate(count=Count('id'))
```

## Development Dependencies

Ensure you have the following packages installed:

- django-extensions
- Werkzeug
- user-agents
- django-ipware
- geoip2

You can install these by running:
```
pip install django-extensions Werkzeug user-agents django-ipware geoip2
```

Also, make sure to add 'django_extensions' to your INSTALLED_APPS in settings.py:

```python
INSTALLED_APPS = [
    # ... other apps ...
    'django_extensions',
]
```

## Note

Ensure compliance with data protection regulations (e.g., GDPR) when collecting and storing visitor data.

## Contributing

[Add information about how to contribute to the project]

## License

[Add license information]
