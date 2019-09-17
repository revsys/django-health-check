from celery import current_app
from django.apps import AppConfig
from django.conf import settings

from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    name = 'health_check.contrib.celery'

    def ready(self):
        from .backends import CeleryHealthCheck

        # To check if we want to check just for default celery queue which is
        # 'celery', you don't need to define anything, else
        # CELERY_QUEUES = [queues used in your project]
        queues = getattr(settings, 'CELERY_QUEUES', [])

        if not queues:
            queues = [queue for queue in current_app.amqp.queues]

        for queue in queues:
            celery_class_name = 'CeleryHealthCheck - ' + queue.title()

            celery_class = type(celery_class_name, (CeleryHealthCheck,), {'queue': queue})
            plugin_dir.register(celery_class)
