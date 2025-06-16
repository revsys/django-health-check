import logging
import smtplib

from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend

from health_check import backends, conf, exceptions

logger = logging.getLogger(__name__)


class MailHealthCheck(backends.BaseHealthCheckBackend):
    """Check that mail backend is working."""

    def check_status(self) -> None:
        """Open and close connection with email server."""
        connection: BaseEmailBackend = get_connection(fail_silently=False)
        connection.timeout = conf.HEALTH_CHECK.get("MAIL_TIMEOUT", 15)
        logger.debug("Trying to open connection to mail backend.")
        try:
            connection.open()
        except smtplib.SMTPException as error:
            self.add_error(
                error=exceptions.ServiceUnavailable(
                    "Failed to open connection with SMTP server",
                ),
                cause=error,
            )
        except ConnectionRefusedError as error:
            self.add_error(
                error=exceptions.ServiceUnavailable(
                    "Connection refused error",
                ),
                cause=error,
            )
        except BaseException as error:
            self.add_error(
                error=exceptions.ServiceUnavailable(
                    f"Unknown error {error.__class__}",
                ),
                cause=error,
            )
        finally:
            connection.close()
        logger.debug("Connection established. Mail backend is healthy.")
