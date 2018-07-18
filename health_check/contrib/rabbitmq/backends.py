import logging
from kombu import Connection
from amqp.exceptions import AccessRefused

from django.conf import settings

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)


class RabbitMQHealthCheck(BaseHealthCheckBackend):
    """
    Healthchecker for RabbitMQ.
    """

    def check_status(self):
        """
        Checks if RabbitMQ service is up by opening and closing
        a broker channel.
        """
        logger.info("Checking for a broker_url on django settings...")

        broker_url = getattr(settings, "BROKER_URL", None)

        try:
            logger.info("Got %s as the broker_url. Connecting to rabbit...")

            conn = Connection(broker_url)

            # opens and closes a channel to rabbitmq to make sure the service is up
            logger.info("Openning a channel to RabbitMQ...")
            conn.channel()

            logger.info("Closing the channel to RabbitMQ...")
            conn.close()

            logger.info("RabbitMQ is healthy.")

        except ConnectionRefusedError as e:
            self.add_error(ServiceUnavailable("Unable to connect to RabbitMQ: Connection was refused."), e)

        except AccessRefused as e:
            self.add_error(ServiceUnavailable("Unable to connect to RabbitMQ: Authentication error."), e)

        except IOError as e:
            self.add_error(ServiceUnavailable("IOError"), e)

        except BaseException as e:
            self.add_error(ServiceUnavailable("Unknown error"), e)
