from django.apps import AppConfig

from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    name = "health_check.contrib.celery_ping"

    def ready(self):
        from .backends import CeleryPingHealthCheck

        plugin_dir.register(CeleryPingHealthCheck)
