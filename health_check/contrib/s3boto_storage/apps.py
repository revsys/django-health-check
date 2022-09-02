from django.apps import AppConfig

from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    name = "health_check.contrib.s3boto_storage"

    def ready(self):
        from .backends import S3BotoStorageHealthCheck

        plugin_dir.register(S3BotoStorageHealthCheck)
