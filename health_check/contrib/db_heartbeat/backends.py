from django.db import connection
from django.db.models import Expression

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable


class SelectOne(Expression):
    """An expression that represents a simple SELECT 1; query."""

    def as_sql(self, compiler, connection):
        return "SELECT 1", []

    def as_oracle(self, compiler, connection):
        return "SELECT 1 FROM DUAL", []


class DatabaseHeartBeatCheck(BaseHealthCheckBackend):
    """Health check that runs a simple SELECT 1; query to test if the database connection is alive."""

    def check_status(self):
        try:
            result = None
            compiler = connection.ops.compiler("SQLCompiler")(SelectOne(), connection, None)
            with connection.cursor() as cursor:
                cursor.execute(*compiler.compile(SelectOne()))
                result = cursor.fetchone()

            if result != (1,):
                raise ServiceUnavailable("Health Check query did not return the expected result.")
        except Exception as e:
            raise ServiceUnavailable(f"Database health check failed: {e}")
