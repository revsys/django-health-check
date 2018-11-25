from django.db import DatabaseError, IntegrityError

from health_check.backends import BaseHealthCheckBackend
from health_check.conf import HEALTH_CHECK
from health_check.exceptions import (
    ServiceReturnedUnexpectedResult, ServiceUnavailable
)
from .models import TestModel

CRITICAL_DB = HEALTH_CHECK['CRITICAL_DB']


class DatabaseBackend(BaseHealthCheckBackend):
    critical_service = CRITICAL_DB

    def check_status(self):
        try:
            obj = TestModel.objects.create(title="test")
            obj.title = "newtest"
            obj.save()
            obj.delete()
        except IntegrityError:
            raise ServiceReturnedUnexpectedResult("Integrity Error")
        except DatabaseError:
            raise ServiceUnavailable("Database error")
