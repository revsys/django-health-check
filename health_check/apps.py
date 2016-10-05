from django.apps import AppConfig


class HealthCheckConfig(AppConfig):
    name = 'health_check'

    def ready(self):
        self.module.autodiscover()
