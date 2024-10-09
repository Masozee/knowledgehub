## Analytics Feature

The Knowledgehub project includes an analytics feature to track visitor data. This feature is integrated into the `app.tools` Django app and uses a separate SQLite database for storing analytics data.

### Features

- Tracks visitor information including:
  - Source (referrer)
  - Device type
  - Browser
  - Operating System
  - Country (based on IP address)
  - IP address
- Uses a separate SQLite database for analytics data
- Integrated with the existing `app.tools` Django app

### Setup

1. Ensure the following dependencies are installed:
   ```
   pip install user-agents django-ipware geoip2
   ```

2. The project settings (`settings.py`) have been updated to include the analytics database:
   ```python
   DATABASES = {
       # ... (existing database configurations)
       'analytics': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'analytics.sqlite3',
       }
   }

   DATABASE_ROUTERS = ['app.tools.routers.AnalyticsRouter']
   ```

3. Run migrations for the analytics models:
   ```
   python manage.py makemigrations tools
   python manage.py migrate --database=analytics
   ```

4. Download a GeoIP database (e.g., GeoLite2-Country.mmdb) and update the path in `app/tools/analytics.py`:
   ```python
   reader = geoip2.database.Reader('/path/to/GeoLite2-Country.mmdb')
   ```

### Usage

To collect visitor data in a view:

```python
from app.tools.analytics import collect_visitor_data

def your_view(request):
    collect_visitor_data(request)
    # Rest of your view logic
    # ...
```

Alternatively, you can create a middleware to automatically collect data for all requests.

### Data Access

Analytics data is stored in the `AnalyticsVisitorData` model in the `app.tools` app. You can query this data using Django's ORM:

```python
from app.tools.models import AnalyticsVisitorData

# Example: Get all visitor data
all_data = AnalyticsVisitorData.objects.using('analytics').all()

# Example: Get visitor count by country
from django.db.models import Count
country_stats = AnalyticsVisitorData.objects.using('analytics').values('country').annotate(count=Count('id'))
```

### Note

Ensure compliance with data protection regulations (e.g., GDPR) when collecting and storing visitor data.
