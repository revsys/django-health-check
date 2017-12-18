from celery import current_app
from django.apps import AppConfig

from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    name = 'health_check.contrib.celery'

    def ready(self):
        from .backends import CeleryHealthCheck

        for queue in current_app.amqp.queues:
            celery_class_name = 'CeleryHealthCheck' + queue.title()

            celery_class = type(celery_class_name, (CeleryHealthCheck,), {'queue': queue})
            plugin_dir.register(celery_class)
