# -*- coding: utf-8 -*-

from django.db import DatabaseError, IntegrityError

from health_check.backends.base import (
    BaseHealthCheckBackend, ServiceReturnedUnexpectedResult, ServiceUnavailable
)
from health_check.db.models import TestModel
from health_check.plugins import plugin_dir


class DjangoDatabaseBackend(BaseHealthCheckBackend):

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


plugin_dir.register(DjangoDatabaseBackend)
