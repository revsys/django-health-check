"""Monitor the health of your Django app and its connected services."""

from . import _version  # noqa
from .cache.backends import CacheBackend as Cache
from .contrib.mail.backends import MailHealthCheck as Mail
from .contrib.psutil.backends import DiskUsage, MemoryUsage
from .contrib.db_heartbeat.backends import DatabaseHeartBeatCheck as Database
from .storage.backends import StorageHealthCheck as Storage

__version__ = _version.__version__
VERSION = _version.__version_tuple__


__all__ = [
    "__version__",
    "VERSION",
    "Cache",
    "Database",
    "DiskUsage",
    "Mail",
    "Storage",
    "MemoryUsage",
]
