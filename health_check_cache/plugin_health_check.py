from django.core.cache.backends.base import CacheKeyWarning
from health_check.backends.base import BaseHealthCheckBackend, HealthCheckStatusType
from health_check.plugins import plugin_dir
from django.core.cache import cache

class CacheBackend(BaseHealthCheckBackend):

    def check_status(self):
        try:
            cache.set('djangohealtcheck_test', 'itworks', 1)
            if cache.get("djangohealtcheck_test") == "itworks":
                return HealthCheckStatusType.working
            else:
                return HealthCheckStatusType.unavailable
        except CacheKeyWarning:
            return HealthCheckStatusType.unexpected_result
        except ValueError:
            return HealthCheckStatusType.unexpected_result
        except Exception:
            return HealthCheckStatusType.unavailable

plugin_dir.register(CacheBackend)