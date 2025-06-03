from django.db import connection

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable


class DatabaseHeartBeatCheck(BaseHealthCheckBackend):
    """Health check that runs a simple SELECT 1; query to test if the database connection is alive."""

    def check_status(self):
        try:
            result = None
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                result = cursor.fetchone()

            if result != (1,):
                raise ServiceUnavailable("Health Check query did not return the expected result.")
        except Exception as e:
            raise ServiceUnavailable(f"Database health check failed: {e}")
