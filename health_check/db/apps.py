from django.apps import AppConfig

from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    name = 'health_check.db'

    def ready(self):
        from .backends import DatabaseBackend
        plugin_dir.register(DatabaseBackend)
