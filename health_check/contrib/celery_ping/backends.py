from celery.app import default_app as app
from django.conf import settings

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable


class CeleryPingHealthCheck(BaseHealthCheckBackend):

    def check_status(self):
        timeout = getattr(settings, 'HEALTHCHECK_CELERY_PING_TIMEOUT', 1)
        try:
            ping_result = app.control.ping(timeout=timeout)
        except IOError as e:
            self.add_error(ServiceUnavailable('IOError'), e)
        except NotImplementedError as exc:
            self.add_error(
                ServiceUnavailable(
                    'NotImplementedError: Make sure CELERY_RESULT_BACKEND is set'
                ),
                exc,
            )
        except BaseException as exc:
            self.add_error(ServiceUnavailable('Unknown error'), exc)
        else:
            if not ping_result:
                self.add_error(
                    ServiceUnavailable('Celery workers unavailable'),
                )
