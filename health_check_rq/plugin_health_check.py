from datetime import datetime, timedelta
from time import sleep
from django.conf import settings
import redis
from rq.worker import Worker


from health_check.backends.base import (
    BaseHealthCheckBackend, ServiceUnavailable
)
from health_check.plugins import plugin_dir


class RqHealthCheck(BaseHealthCheckBackend):

    def check_status(self):
        conn = redis.StrictRedis(**settings.RQ)
        worker_count = 0
        for worker in Worker.all(connection=conn):
            if conn.ttl(worker.key) > 0:
                worker_count += 1

        if worker_count <= 0:
            raise ServiceUnavailable("Unknown error")
        return True

plugin_dir.register(RqHealthCheck)

