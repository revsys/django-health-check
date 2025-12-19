import locale
import socket

import psutil

from health_check.backends import BaseHealthCheckBackend
from health_check.conf import HEALTH_CHECK
from health_check.exceptions import ServiceReturnedUnexpectedResult, ServiceWarning

host = socket.gethostname()

DISK_USAGE_MAX = HEALTH_CHECK["DISK_USAGE_MAX"]
MEMORY_MIN = HEALTH_CHECK["MEMORY_MIN"]


class DiskUsage(BaseHealthCheckBackend):
    def check_status(self):
        try:
            du = psutil.disk_usage("/")
            if DISK_USAGE_MAX and du.percent >= DISK_USAGE_MAX:
                raise ServiceWarning(f"{host} {du.percent}% disk usage exceeds {DISK_USAGE_MAX}%")
        except ValueError as e:
            self.add_error(ServiceReturnedUnexpectedResult("ValueError"), e)


class MemoryUsage(BaseHealthCheckBackend):
    def check_status(self):
        try:
            memory = psutil.virtual_memory()
            if MEMORY_MIN and memory.available < (MEMORY_MIN * 1024 * 1024):
                locale.setlocale(locale.LC_ALL, "")
                avail = f"{int(memory.available / 1024 / 1024):n}"
                threshold = f"{MEMORY_MIN:n}"
                raise ServiceWarning(f"{host} {avail} MB available RAM below {threshold} MB")
        except ValueError as e:
            self.add_error(ServiceReturnedUnexpectedResult("ValueError"), e)
