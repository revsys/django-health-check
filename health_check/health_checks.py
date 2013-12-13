from health_check.backends.base import BaseHealthCheckBackend, ServiceUnavailable, ServiceReturnedUnexpectedResult, StorageHealthCheck
from health_check.plugins import plugin_dir
from health_check.models import TestModel
from health_check.tasks import add

from datetime import datetime, timedelta
from time import sleep
import random

from django.core.cache.backends.base import CacheKeyWarning
from django.core.cache import cache
from django.db import DatabaseError, IntegrityError
from django.conf import settings


class CacheBackendCheck(BaseHealthCheckBackend):

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
        raise ServiceUnavailable("Unknown error")

plugin_dir.register(CeleryHealthCheck)


class DjangoDatabaseBackend(BaseHealthCheckBackend):

    def check_status(self):
        try:
            obj = TestModel.objects.create(title="test")
            obj.title = "newtest"
            obj.save()
            obj.delete()
            return True
        except IntegrityError:
            raise ServiceReturnedUnexpectedResult("Integrity Error")
        except DatabaseError, e:
            raise ServiceUnavailable("Database error")

plugin_dir.register(DjangoDatabaseBackend)


class DefaultFileStorageHealthCheck(StorageHealthCheck):
    storage = settings.DEFAULT_FILE_STORAGE

plugin_dir.register(DefaultFileStorageHealthCheck)
