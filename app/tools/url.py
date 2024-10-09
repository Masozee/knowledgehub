from django.urls import path
from .views import test_logging

urlpatterns = [
    # ... your other URL patterns ...
    path('test-logging/', test_logging, name='test_logging'),
]