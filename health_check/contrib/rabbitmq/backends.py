import logging

import pika
from django.conf import settings
from pika.exceptions import ConnectionClosed, ProbableAuthenticationError

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)


class RabbitMQHealthCheck(BaseHealthCheckBackend):
    """
    Healthchecker for RabbitMQ.

    """

    def __get_broker_url(self):
        """
        Gets the broker url based on django.confg.settings dictionary.

        """
        broker_url = getattr(settings, "BROKER_URL", None)

        if broker_url is None:
            logger.info("Variable BROKER_URL not found on django.conf.settings...")

            broker_host = getattr(settings, "BROKER_HOST", "localhost")
            broker_username = getattr(settings, "BROKER_USERNAME", "user")
            broker_password = getattr(settings, "BROKER_PASSWORD", "password")
            broker_port = getattr(settings, "BROKER_PORT", "5672")
            broker_vhost = getattr(settings, "BROKER_VHOST", "/")

            # corrects vhost if set to /
            broker_vhost = "" if broker_vhost == "/" else broker_vhost

            broker_url = "amqp://%s:%s@%s:%s/%s" % (
                broker_username,
                broker_password,
                broker_host,
                broker_port,
                broker_vhost,
            )

        return broker_url

    def check_status(self):
        """
        Checks if RabbitMQ service is up by opening and closing
        a broker channel.

        """

        try:

            logger.info("Checking for a broker_url on django settings...")

            broker_url = self.__get_broker_url()

            logger.info("Got broker_url: %s. Creating a connection to the broker...", broker_url)

            conn = pika.BlockingConnection(pika.URLParameters(broker_url))

            # opens and closes a channel to rabbitmq to make sure the service is up
            logger.info("Openning a channel to RabbitMQ...")
            conn.channel()

            logger.info("Closing the channel to RabbitMQ...")
            conn.close()

            logger.info("RabbitMQ is healthy.")

        except ConnectionClosed as e:
            self.add_error(ServiceUnavailable("Unable to connect to RabbitMQ: Connection refused."), e)

        except ProbableAuthenticationError as e:
            self.add_error(
                ServiceUnavailable("Unable to connect to RabbitMQ: Authentication error. Check your django config."), e
            )

        except IOError as e:
            self.add_error(ServiceUnavailable("IOError"), e)

        except BaseException as e:
            self.add_error(ServiceUnavailable("Unknown error"), e)
