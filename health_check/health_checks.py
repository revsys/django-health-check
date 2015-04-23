from health_check.backends.base import BaseHealthCheckBackend, ServiceUnavailable, ServiceReturnedUnexpectedResult, StorageHealthCheck
from health_check.plugins import plugin_dir
from health_check.models import TestModel
from health_check.tasks import add

from datetime import datetime, timedelta
from time import sleep
import random
import logging

from django.core.cache.backends.base import CacheKeyWarning
from django.core.cache import cache
from django.db import DatabaseError, IntegrityError
from django.conf import settings


class CacheBackendCheck(BaseHealthCheckBackend):

    def check_status(self):
        try:
            expected = 'itworks'
            cache.set('djangohealtcheck_test', expected, 1)
            got = cache.get("djangohealtcheck_test")
            if got == expected:
                return True
            else:
                raise ServiceUnavailable("Cache key does not match. Got %s, expected %s" % (got, expected))
        except CacheKeyWarning as e:
            raise ServiceReturnedUnexpectedResult("Cache key warning: %s" % e)
        except ValueError as e:
            raise ServiceReturnedUnexpectedResult("ValueError: %s" % e)
        except Exception as e:
            raise ServiceUnavailable("Unknown cache exception: %s" % e)

plugin_dir.register(CacheBackendCheck)


class CeleryHealthCheck(BaseHealthCheckBackend):

    def check_status(self):
        try:
            result = add.apply_async(args=[4, 4], expires=datetime.now() + timedelta(seconds=3), connect_timeout=3)
            now = datetime.now()
            while (now + timedelta(seconds=3)) > datetime.now():
                if result.result == 8:
                    return True
                sleep(0.5)
        except IOError:
            pass
        raise ServiceUnavailable("Celery task took > 3 seconds to complete.")

plugin_dir.register(CeleryHealthCheck)


class DjangoDatabaseBackend(BaseHealthCheckBackend):

    def check_status(self):
        try:
            obj = TestModel.objects.create(title="test")
            obj.title = "newtest"
            obj.save()
            obj.delete()
            return True
        except IntegrityError as e:
            raise ServiceReturnedUnexpectedResult("Integrity Error: %s" % e)
        except DatabaseError as e:
            raise ServiceUnavailable("Database error: %s" % e)

plugin_dir.register(DjangoDatabaseBackend)