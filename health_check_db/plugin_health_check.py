from health_check.backends.base import BaseHealthCheckBackend, ServiceUnavailable, ServiceReturnedUnexpectedResult
from health_check_db.models import TestModel
from django.db import DatabaseError, IntegrityError
from health_check.plugins import plugin_dir

class DjangoDatabaseBackend(BaseHealthCheckBackend):

    def check_status(self):
        try:
            obj = TestModel.objects.create(title="test")
            obj.title = "newtest"
            obj.save()
            obj.delete()
            return True
        except IntegrityError as e:
            raise ServiceReturnedUnexpectedResult("Integrity Error") from e
        except DatabaseError as e:
            raise ServiceUnavailable("Database error") from e

plugin_dir.register(DjangoDatabaseBackend)
