from django.apps import AppConfig

from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    name = 'health_check.cache'

    def ready(self):
        from .backends import CacheBackend
        plugin_dir.register(CacheBackend)
