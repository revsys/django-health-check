from django.db import DatabaseError, IntegrityError, transaction

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceReturnedUnexpectedResult, ServiceUnavailable

from .models import TestModel


class DatabaseBackend(BaseHealthCheckBackend):
    database_name = ""

    def __init__(self, database_name: str = "") -> None:
        super().__init__()
        self.database_name = database_name or None

    def check_status(self):
        try:
            with transaction.atomic(using=self.database_name):
                obj = TestModel.objects.create(title="test")
                obj.title = "newtest"
                obj.save()
                obj.delete()
        except IntegrityError:
            raise ServiceReturnedUnexpectedResult("Integrity Error")
        except DatabaseError:
            raise ServiceUnavailable("Database error")

    def identifier(self) -> str:
        if not self.database_name:
            return super().identifier()

        return f"{self.__class__.__name__}[{self.database_name}]"
