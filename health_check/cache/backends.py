from django.conf import settings
from django.core.cache import CacheKeyWarning, caches

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceReturnedUnexpectedResult, ServiceUnavailable

try:
    # Exceptions thrown by Redis do not subclass builtin exceptions like ConnectionError.
    # Additionally, not only connection errors (ConnectionError -> RedisError) can be raised,
    # but also errors for time-outs (TimeoutError -> RedisError)
    # and if the backend is read-only (ReadOnlyError -> ResponseError -> RedisError).
    # Since we know what we are trying to do here, we are not picky and catch the global exception RedisError.
    from redis.exceptions import RedisError
except ModuleNotFoundError:
    # In case Redis is not installed and another cache backend is used.
    class RedisError(Exception):
        pass


class CacheBackend(BaseHealthCheckBackend):
    def __init__(self, backend="default"):
        super().__init__()
        self.backend = backend
        self.cache_key = getattr(settings, "HEALTHCHECK_CACHE_KEY", "djangohealthcheck_test")

    def identifier(self):
        return f"Cache backend: {self.backend}"

    def check_status(self):
        cache = caches[self.backend]

        try:
            cache.set(self.cache_key, "itworks")
            if not cache.get(self.cache_key) == "itworks":
                raise ServiceUnavailable(f"Cache key {self.cache_key} does not match")
        except CacheKeyWarning as e:
            self.add_error(ServiceReturnedUnexpectedResult("Cache key warning"), e)
        except ValueError as e:
            self.add_error(ServiceReturnedUnexpectedResult("ValueError"), e)
        except (ConnectionError, RedisError) as e:
            self.add_error(ServiceReturnedUnexpectedResult("Connection Error"), e)
