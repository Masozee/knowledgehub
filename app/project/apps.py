from django.apps import AppConfig


class ProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.project'

    def ready(self):
        """Import signal handlers when the app is ready"""
        import app.project.signals