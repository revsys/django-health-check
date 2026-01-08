from collections import namedtuple
from unittest import mock

import pytest

from health_check.contrib.psutil.backends import DiskUsage

# psutil.disk_usage() returns a namedtuple
sdiskusage = namedtuple("sdiskusage", ("total", "used", "free", "percent"))


def mock_disk_usage(path):
    """Mock function to simulate psutil.disk_usage() in a container/host environment."""
    if path == "/":
        # Default path (container) with high disk space
        return sdiskusage(total=100, used=97, free=3, percent=97)
    elif path == "/host/":
        # Custom path (host) with low disk usage
        return sdiskusage(total=100, used=5, free=95, percent=5)
    else:
        # No other disk in the system
        raise FileNotFoundError(f"No such file or directory: '{path}'")


@mock.patch("health_check.contrib.psutil.backends.psutil.disk_usage", mock_disk_usage)
class TestDiskUsage:
    def test_default_path(self):
        du = DiskUsage()
        du.run_check()
        assert du.errors
        assert "97% disk usage exceeds 90%" in str(du.errors[0])

    @mock.patch.multiple("health_check.contrib.psutil.backends", DISK_USAGE_PATH="/host/")
    def test_custom_path_when_valid(self):
        du = DiskUsage()
        du.run_check()
        assert not du.errors

    @mock.patch.multiple("health_check.contrib.psutil.backends", DISK_USAGE_PATH="*NOT A PATH*")
    def test_custom_path_when_invalid(self):
        du = DiskUsage()
        with pytest.raises(FileNotFoundError):
            du.run_check()
