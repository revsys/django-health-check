from django.apps import AppConfig

from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    name = "health_check.contrib.http_ping"

    def ready(self):
        from .backends import HTTPPingHealthCheck

        plugin_dir.register(HTTPPingHealthCheck)
