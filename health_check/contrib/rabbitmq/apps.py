from django.apps import AppConfig

from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    name = "health_check.contrib.rabbitmq"

    def ready(self):
        from .backends import RabbitMQHealthCheck

        plugin_dir.register(RabbitMQHealthCheck)
