from django.core.cache import CacheKeyWarning, caches

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import (
    ServiceReturnedUnexpectedResult, ServiceUnavailable
)


class CacheBackend(BaseHealthCheckBackend):
    def __init__(self, backend=''):
        super().__init__()
        self.backend = backend or 'default'

    def identifier(self):
        return "Cache backend: %s" % self.backend

    def check_status(self):
        cache = caches[self.backend]

        try:
            cache.set('djangohealtcheck_test', 'itworks', 1)
            if not cache.get("djangohealtcheck_test") == "itworks":
                raise ServiceUnavailable("Cache key does not match")
        except CacheKeyWarning as e:
            self.add_error(ServiceReturnedUnexpectedResult("Cache key warning"), e)
        except ValueError as e:
            self.add_error(ServiceReturnedUnexpectedResult("ValueError"), e)
        except ConnectionError as e:
            self.add_error(ServiceReturnedUnexpectedResult("Connection Error"), e)
