from health_check.plugins import plugin_dir
from health_check.backends.base import BaseHealthCheckBackend, ServiceUnavailable
from health_check_celery.tasks import add
from datetime import datetime, timedelta
from time import sleep


class CeleryHealthCheck(BaseHealthCheckBackend):

    def check_status(self):
        try:
            result = add.apply_async(args=[4, 4], expires=datetime.now() + timedelta(seconds=3), connect_timeout=3)
            now = datetime.now()
            while (now + timedelta(seconds=3)) > datetime.now():
                if result.result == 8:
                    return True
                sleep(0.5)
        except IOError:
            pass
        raise ServiceUnavailable("Unknown error")

plugin_dir.register(CeleryHealthCheck)
