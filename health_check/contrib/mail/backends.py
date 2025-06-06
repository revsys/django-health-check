import logging

from django.core.mail import get_connection

from health_check.backends import BaseHealthCheckBackend
from health_check.conf import HEALTH_CHECK
from health_check.exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)


class MailHealthCheck(BaseHealthCheckBackend):
    """Check that mail backend is working."""

    def check_status(self) -> None:
        """Open and close connection email server."""
        try:
            connection = get_connection(fail_silently=False)
            connection.timeout = HEALTH_CHECK.get("MAIL_TIMEOUT", 15)
            logger.debug("Trying to open connection to mail backend.")
            connection.open()
            connection.close()
            logger.debug("Connection established. Mail backend is healthy.")
        except Exception as error:
            self.add_error(
                error=ServiceUnavailable(error),
                cause=error,
            )
