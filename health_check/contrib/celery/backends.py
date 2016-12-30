from datetime import datetime, timedelta

from django.conf import settings

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import (
    ServiceReturnedUnexpectedResult, ServiceUnavailable
)

from .tasks import add


class CeleryHealthCheck(BaseHealthCheckBackend):
    def check_status(self):
        timeout = getattr(settings, 'HEALTHCHECK_CELERY_TIMEOUT', 3)

        try:
            result = add.apply_async(
                args=[4, 4],
                expires=datetime.now() + timedelta(seconds=timeout)
            )
            result.get(timeout=timeout)
            if result.result != 8:
                self.add_error(ServiceReturnedUnexpectedResult("Celery returned wrong result"))
        except IOError as e:
            self.add_error(ServiceUnavailable("IOError"), e)
        except BaseException as e:
            self.add_error(ServiceUnavailable("Unknown error"), e)
