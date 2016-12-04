# -*- coding: utf-8 -*-
import logging

from django.core.cache import cache
from django.core.cache.backends.base import CacheKeyWarning

from health_check.backends.base import BaseHealthCheckBackend
from health_check.plugins import plugin_dir


class CacheBackend(BaseHealthCheckBackend):
    logger = logging.getLogger(__name__)

    def check_status(self):
        try:
            cache.set('djangohealtcheck_test', 'itworks', 1)
            if cache.get("djangohealtcheck_test") == "itworks":
                return True
            else:
                self.unavailable("Cache key does not match")
        except CacheKeyWarning:
            self.unexpected("Cache key warning")
        except ValueError:
            self.unexpected("ValueError")
        except Exception as e:
            self.unavailable("Unknown exception {}".format(e))

plugin_dir.register(CacheBackend)
