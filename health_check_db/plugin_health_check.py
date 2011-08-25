from health_check.backends.base import BaseHealthCheckBackend, HealthCheckStatusType
from health_check.models import TestModel
from django.db import DatabaseError, IntegrityError
from health_check.plugins import plugin_dir

class DjangoDatabaseBackend(BaseHealthCheckBackend):

    def check_status(self):
        try:
            obj = TestModel.objects.create(title="test")
            obj.title = "newtest"
            obj.save()
            obj.delete()
            return HealthCheckStatusType.working
        except IntegrityError:
            return HealthCheckStatusType.unexpected_result
        except DatabaseError:
            return HealthCheckStatusType.unavailable

plugin_dir.register(DjangoDatabaseBackend)