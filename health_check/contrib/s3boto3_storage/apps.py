from django.apps import AppConfig

from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    name = 'health_check.contrib.s3boto3_storage'

    def ready(self):
        from .backends import S3Boto3StorageHealthCheck
        plugin_dir.register(S3Boto3StorageHealthCheck)
