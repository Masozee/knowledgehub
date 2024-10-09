# my_project/router.py

class DefaultRouter:
    """
    A router to control all database operations on models for the
    default database.
    """
    route_app_labels = {'auth', 'contenttypes', 'sessions', 'admin', 'people'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read models go to default.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write models go to default.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects are in the specified apps.
        """
        if (
            obj1._meta.app_label in self.route_app_labels and
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the specified apps only appear in the 'default' database.
        """
        if app_label in self.route_app_labels:
            return db == 'default'
        return None

class LogsRouter:
    """
    A router to control all database operations for logs.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read logs go to logs_db.
        """
        if model._meta.app_label == 'logs':
            return 'logs_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write logs go to logs_db.
        """
        if model._meta.app_label == 'logs':
            return 'logs_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects are in the logs app.
        """
        if obj1._meta.app_label == 'logs' and obj2._meta.app_label == 'logs':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Prevent migrations for logs_db.
        """
        if db == 'logs_db':
            return False
        return None

class AnalyticsRouter:
    """
    A router to control all database operations on models in the
    analytics application.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read analytics models go to analytics_db.
        """
        if model._meta.app_label == 'analytics':
            return 'analytics'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write analytics models go to analytics_db.
        """
        if model._meta.app_label == 'analytics':
            return 'analytics'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects are in the analytics app.
        """
        if obj1._meta.app_label == 'analytics' and obj2._meta.app_label == 'analytics':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the analytics app only appears in the 'analytics'
        database.
        """
        if app_label == 'analytics':
            return db == 'analytics'
        return None