import logging
from datetime import datetime, timedelta
from time import sleep

from django.conf import settings

from health_check.backends.base import (
    BaseHealthCheckBackend, ServiceUnavailable
)
from health_check.plugins import plugin_dir
from health_check_celery3.tasks import add

logger = logging.getLogger(__name__)


class CeleryHealthCheck(BaseHealthCheckBackend):

    def check_status(self):
        timeout = getattr(settings, 'HEALTHCHECK_CELERY_TIMEOUT', 3)

        try:
            result = add.apply_async(
                args=[4, 4],
                expires=datetime.now() + timedelta(seconds=timeout)
            )
            now = datetime.now()
            while (now + timedelta(seconds=3)) > datetime.now():
                print("            checking....")
                if result.ready():
                    result.forget()
                    return True
                sleep(0.5)
        except IOError:
            logger.exception("IOError")
            raise ServiceUnavailable("IOError")
        except:
            logger.exception("Unknown Error")
            raise ServiceUnavailable("Unknown error")

        logger.error(
            u'Celery task did not complete successfully. '
            u'Verify celery is running'
        )
        raise ServiceUnavailable("Unknown error")

plugin_dir.register(CeleryHealthCheck)
