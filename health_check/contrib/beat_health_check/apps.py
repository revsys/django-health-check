from django.apps import AppConfig
from health_check.plugins import plugin_dir


class HealthchecksConfig(AppConfig):
    name = "contrib.beat_health_check"

    def ready(self):
        from .backends import CeleryBeatHealthCheck

        plugin_dir.register(CeleryBeatHealthCheck)
