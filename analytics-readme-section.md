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

#claude logo
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" class="w-full fill-current"><path d="m19.6 66.5 19.7-11 .3-1-.3-.5h-1l-3.3-.2-11.2-.3L14 53l-9.5-.5-2.4-.5L0 49l.2-1.5 2-1.3 2.9.2 6.3.5 9.5.6 6.9.4L38 49.1h1.6l.2-.7-.5-.4-.4-.4L29 41l-10.6-7-5.6-4.1-3-2-1.5-2-.6-4.2 2.7-3 3.7.3.9.2 3.7 2.9 8 6.1L37 36l1.5 1.2.6-.4.1-.3-.7-1.1L33 25l-6-10.4-2.7-4.3-.7-2.6c-.3-1-.4-2-.4-3l3-4.2L28 0l4.2.6L33.8 2l2.6 6 4.1 9.3L47 29.9l2 3.8 1 3.4.3 1h.7v-.5l.5-7.2 1-8.7 1-11.2.3-3.2 1.6-3.8 3-2L61 2.6l2 2.9-.3 1.8-1.1 7.7L59 27.1l-1.5 8.2h.9l1-1.1 4.1-5.4 6.9-8.6 3-3.5L77 13l2.3-1.8h4.3l3.1 4.7-1.4 4.9-4.4 5.6-3.7 4.7-5.3 7.1-3.2 5.7.3.4h.7l12-2.6 6.4-1.1 7.6-1.3 3.5 1.6.4 1.6-1.4 3.4-8.2 2-9.6 2-14.3 3.3-.2.1.2.3 6.4.6 2.8.2h6.8l12.6 1 3.3 2 1.9 2.7-.3 2-5.1 2.6-6.8-1.6-16-3.8-5.4-1.3h-.8v.4l4.6 4.5 8.3 7.5L89 80.1l.5 2.4-1.3 2-1.4-.2-9.2-7-3.6-3-8-6.8h-.5v.7l1.8 2.7 9.8 14.7.5 4.5-.7 1.4-2.6 1-2.7-.6-5.8-8-6-9-4.7-8.2-.5.4-2.9 30.2-1.3 1.5-3 1.2-2.5-2-1.4-3 1.4-6.2 1.6-8 1.3-6.4 1.2-7.9.7-2.6v-.2H49L43 72l-9 12.3-7.2 7.6-1.7.7-3-1.5.3-2.8L24 86l10-12.8 6-7.9 4-4.6-.1-.5h-.3L17.2 77.4l-4.7.6-2-2 .2-3 1-1 8-5.5Z"></path></svg>

