import logging

from django.db import DatabaseError, IntegrityError

from health_check.backends.base import (
    BaseHealthCheckBackend, ServiceReturnedUnexpectedResult, ServiceUnavailable
)
from health_check.plugins import plugin_dir
from health_check_db.models import TestModel

logger = logging.getLogger(__name__)


class DjangoDatabaseBackend(BaseHealthCheckBackend):

    def check_status(self):
        try:
            obj = TestModel.objects.create(title="test")
            obj.title = "newtest"
            obj.save()
            obj.delete()
            return True
        except IntegrityError:
            logger.exception("Integrity Error")
            raise ServiceReturnedUnexpectedResult("Integrity Error")
        except DatabaseError:
            logger.exception("Database Error")
            raise ServiceUnavailable("Database error")

plugin_dir.register(DjangoDatabaseBackend)
