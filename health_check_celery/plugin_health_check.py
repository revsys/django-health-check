from datetime import datetime, timedelta
from time import sleep

from django.conf import settings

from health_check.backends.base import (
    BaseHealthCheckBackend, ServiceUnavailable
)
from health_check.plugins import plugin_dir
from health_check_celery.tasks import add


class CeleryHealthCheck(BaseHealthCheckBackend):

    def check_status(self):
        timeout = getattr(settings, 'HEALTHCHECK_CELERY_TIMEOUT', 3)
        expires = datetime.now() + timedelta(seconds=timeout)
        try:
            result = add.apply_async(args=[4, 4], expires=expires, connect_timeout=timeout)
            now = datetime.now()
            while (now + timedelta(seconds=3)) > datetime.now():
                if result.result == 8:
                    return True
                sleep(0.5)
        except IOError:
            pass
        raise ServiceUnavailable("Unknown error")

plugin_dir.register(CeleryHealthCheck)
