from django.core.cache import cache
from django.core.cache.backends.base import CacheKeyWarning

from health_check.backends.base import (
    BaseHealthCheckBackend, ServiceReturnedUnexpectedResult, ServiceUnavailable
)
from health_check.plugins import plugin_dir


class CacheBackend(BaseHealthCheckBackend):

    def check_status(self):
        try:
            cache.set('djangohealtcheck_test', 'itworks', 1)
            if cache.get("djangohealtcheck_test") == "itworks":
                return True
            else:
                raise ServiceUnavailable("Cache key does not match")
        except CacheKeyWarning:
            raise ServiceReturnedUnexpectedResult("Cache key warning")
        except ValueError:
            raise ServiceReturnedUnexpectedResult("ValueError")
        except Exception:
            raise ServiceUnavailable("Unknown exception")

plugin_dir.register(CacheBackend)
