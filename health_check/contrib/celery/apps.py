from celery import current_app
from django.apps import AppConfig
from django.conf import settings
import logging


from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    name = 'health_check.contrib.celery'

    def ready(self):
        from .backends import CeleryHealthCheck
        if hasattr(settings, "HEALTHCHECK_CELERY_TIMEOUT"):
            logger = logging.getLogger('health-check')
            logger.warn("HEALTHCHECK_CELERY_TIMEOUT is depricated and may be removed in the "
                        "future. Please use HEALTHCHECK_CELERY_RESULT_TIMEOUT and "
                        "HEALTHCHECK_CELERY_QUEUE_TIMEOUT instead.")

        for queue in current_app.amqp.queues:
            celery_class_name = 'CeleryHealthCheck' + queue.title()

            celery_class = type(celery_class_name, (CeleryHealthCheck,), {'queue': queue})
            plugin_dir.register(celery_class)
