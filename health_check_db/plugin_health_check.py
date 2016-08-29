from django.db import DatabaseError, IntegrityError

from health_check.backends.base import (
    BaseHealthCheckBackend, ServiceReturnedUnexpectedResult, ServiceUnavailable
)
from health_check.plugins import plugin_dir
from health_check_db.models import TestModel


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
        except DatabaseError:
            raise ServiceUnavailable("Database Error")
        except Exception:
            raise ServiceUnavailable("Unknown Error")

plugin_dir.register(DjangoDatabaseBackend)
