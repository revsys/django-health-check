# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from time import sleep

from django.conf import settings

from health_check.backends.base import BaseHealthCheckBackend
from health_check.plugins import plugin_dir
from health_check_celery3.tasks import add


class CeleryHealthCheck(BaseHealthCheckBackend):
    logger = logging.getLogger(__name__)

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
                    try:
                        result.forget()
                    except NotImplementedError:
                        pass
                    return True
                sleep(0.5)
        except IOError:
            self.unavailable("IOError")
        except Exception as e:
            self.unavailable("Unknown Error {}".format(e))

        self.unavailable(
            'Celery task did not complete successfully. '
            'Verify celery is running'
        )

plugin_dir.register(CeleryHealthCheck)
