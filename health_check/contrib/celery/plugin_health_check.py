# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from time import sleep

from django.conf import settings

from health_check.backends.base import (
    BaseHealthCheckBackend, ServiceUnavailable
)
from health_check.plugins import plugin_dir
from .tasks import add


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
                    try:
                        result.forget()
                    except NotImplementedError:
                        pass
                    return True
                sleep(0.5)
        except IOError:
            raise ServiceUnavailable("IOError")
        except:
            raise ServiceUnavailable("Unknown error")

        raise ServiceUnavailable("Unknown error")


plugin_dir.register(CeleryHealthCheck)
