from django.apps import AppConfig

from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    name = "health_check.contrib.mail"

    def ready(self):
        from .backends import MailHealthCheck

        plugin_dir.register(MailHealthCheck)
