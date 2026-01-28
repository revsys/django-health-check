import dataclasses
import locale
import socket

import psutil

from health_check.backends import BaseHealthCheckBackend
from health_check.conf import HEALTH_CHECK
from health_check.exceptions import ServiceReturnedUnexpectedResult, ServiceWarning

host = socket.gethostname()


@dataclasses.dataclass()
class DiskUsage(BaseHealthCheckBackend):
    """
    Check system disk usage.

    Args:
        max_disk_usage_percent: Maximum disk usage in percent or None to disable the check.

    """

    max_disk_usage_percent: float | None = HEALTH_CHECK["DISK_USAGE_MAX"]

    def check_status(self):
        try:
            du = psutil.disk_usage("/")
            if self.max_disk_usage_percent and du.percent >= self.max_disk_usage_percent:
                raise ServiceWarning(f"{host} {du.percent}% disk usage exceeds {self.max_disk_usage_percent}%")
        except ValueError as e:
            self.add_error(ServiceReturnedUnexpectedResult("ValueError"), e)


@dataclasses.dataclass()
class MemoryUsage(BaseHealthCheckBackend):
    """
    Check system memory usage.

    Args:
        min_bytes_available: Minimum available memory in bytes or None to disable the check.
        max_memory_usage_percent: Maximum memory usage in percent or None to disable the check.

    """

    min_bytes_available: float | None = HEALTH_CHECK["MEMORY_MIN"] * 1024 * 1024
    max_memory_usage_percent: float | None = 90.0

    def check_status(self):
        try:
            memory = psutil.virtual_memory()
            if self.min_bytes_available and memory.available < (self.min_bytes_available * 1024 * 1024):
                locale.setlocale(locale.LC_ALL, "")
                avail = f"{int(memory.available / 1024 / 1024):n}"
                threshold = f"{self.min_bytes_available:n}"
                raise ServiceWarning(f"{host} {avail} MB available RAM below {threshold} MB")
            if self.max_memory_usage_percent and memory.percent >= self.max_memory_usage_percent:
                raise ServiceWarning(f"{host} {memory.percent}% memory usage exceeds {self.max_memory_usage_percent}%")
        except ValueError as e:
            self.add_error(ServiceReturnedUnexpectedResult("ValueError"), e)
