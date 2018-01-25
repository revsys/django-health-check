import locale
import socket

from django.conf import settings

import psutil
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import (
    ServiceReturnedUnexpectedResult, ServiceWarning
)

host = socket.gethostname()

if hasattr(settings, 'HEALTH_CHECK'):
    DISK_USAGE_MAX = settings.HEALTH_CHECK.get('DISK_USAGE_MAX', 90)  # in %
    MEMORY_MIN = settings.HEALTH_CHECK.get('MEMORY_MIN', 100)  # in MB
else:
    DISK_USAGE_MAX = 90  # in %
    MEMORY_MIN = 100  # in MB


class DiskUsage(BaseHealthCheckBackend):
    def check_status(self):
        try:
            du = psutil.disk_usage('/')
            if DISK_USAGE_MAX and du.percent >= DISK_USAGE_MAX:
                raise ServiceWarning(
                    f"{host} {du.percent}% disk usage exceeds {DISK_USAGE_MAX}%"
                )
        except ValueError as e:
            self.add_error(ServiceReturnedUnexpectedResult("ValueError"), e)


class MemoryUsage(BaseHealthCheckBackend):
    def check_status(self):
        try:
            memory = psutil.virtual_memory()
            if MEMORY_MIN and memory.available < (MEMORY_MIN * 1024 * 1024):
                locale.setlocale(locale.LC_ALL, '')
                avail = '{:n}'.format(int(memory.available / 1024 / 1024))
                threshold = '{:n}'.format(MEMORY_MIN)
                raise ServiceWarning(
                    f"{host} {avail} MB available RAM below {threshold} MB"
                )
        except ValueError as e:
            self.add_error(ServiceReturnedUnexpectedResult("ValueError"), e)
