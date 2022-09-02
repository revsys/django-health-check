import logging

from amqp.exceptions import AccessRefused
from django.conf import settings
from kombu import Connection

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)


class RabbitMQHealthCheck(BaseHealthCheckBackend):
    """Health check for RabbitMQ."""

    def check_status(self):
        """Check RabbitMQ service by opening and closing a broker channel."""
        logger.debug("Checking for a broker_url on django settings...")

        broker_url = getattr(settings, "BROKER_URL", None)

        logger.debug("Got %s as the broker_url. Connecting to rabbit...", broker_url)

        logger.debug("Attempting to connect to rabbit...")
        try:
            # conn is used as a context to release opened resources later
            with Connection(broker_url) as conn:
                conn.connect()  # exceptions may be raised upon calling connect
        except ConnectionRefusedError as e:
            self.add_error(
                ServiceUnavailable(
                    "Unable to connect to RabbitMQ: Connection was refused."
                ),
                e,
            )

        except AccessRefused as e:
            self.add_error(
                ServiceUnavailable(
                    "Unable to connect to RabbitMQ: Authentication error."
                ),
                e,
            )

        except IOError as e:
            self.add_error(ServiceUnavailable("IOError"), e)

        except BaseException as e:
            self.add_error(ServiceUnavailable("Unknown error"), e)
        else:
            logger.debug("Connection established. RabbitMQ is healthy.")
