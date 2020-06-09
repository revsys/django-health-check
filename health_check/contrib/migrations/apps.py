from django.apps import AppConfig

from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    name = "health_check.contrib.migrations"

    def ready(self):
        from .backends import MigrationsHealthCheck

        plugin_dir.register(MigrationsHealthCheck)
