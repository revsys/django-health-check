from django.apps import AppConfig
from django.conf import settings

from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "health_check.db"

    def ready(self):
        from .backends import DatabaseBackend

        plugin_dir.register(DatabaseBackend)

        for database_name in settings.DATABASES.keys():
            plugin_dir.register(DatabaseBackend, database_name=database_name)
