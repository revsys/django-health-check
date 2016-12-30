from django.core.cache import cache
from django.core.cache.backends.base import CacheKeyWarning

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable, ServiceReturnedUnexpectedResult
from health_check.plugins import plugin_dir


class CacheBackend(BaseHealthCheckBackend):
    def check_status(self):
        try:
            cache.set('djangohealtcheck_test', 'itworks', 1)
            if not cache.get("djangohealtcheck_test") == "itworks":
                raise ServiceUnavailable("Cache key does not match")
        except CacheKeyWarning as e:
            self.add_error(ServiceReturnedUnexpectedResult("Cache key warning"), e)
        except ValueError as e:
            self.add_error(ServiceReturnedUnexpectedResult("ValueError"), e)


plugin_dir.register(CacheBackend)
