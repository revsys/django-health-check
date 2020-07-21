from django.apps import AppConfig

from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    name = "health_check.contrib.mongo"

    def ready(self):
        from .backends import MongoHealthCheck

        plugin_dir.register(MongoHealthCheck)
