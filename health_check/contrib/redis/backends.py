import logging

from django.conf import settings
from redis import exceptions, Redis

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)


class RedisHealthCheck(BaseHealthCheckBackend):
    """Health check for Redis."""

    redis_host = getattr(settings, "REDIS_HOST", 'localhost')
    redis_port = getattr(settings, "REDIS_PORT", '6379')

    def check_status(self):
        """Check Redis service by pinging the redis instance with a redis connection."""
        logger.debug("Got %s as the redis_url. Connecting to redis...", self.redis_host)

        logger.debug("Attempting to connect to redis...")
        try:
            # Keeping the timeout 2 sec, so that connection closes after health check
            conn = Redis(
                host=self.redis_host,
                port=self.redis_port,
                socket_connect_timeout=2
            )
            conn.ping()  # exceptions may be raised upon ping
        except ConnectionRefusedError as e:
            self.add_error(ServiceUnavailable("Unable to connect to Redis: Connection was refused."), e)
        except exceptions.TimeoutError as e:
            self.add_error(ServiceUnavailable("Unable to connect to Redis: Timeout."), e)
        except exceptions.ConnectionError as e:
            self.add_error(ServiceUnavailable("Unable to connect to Redis: Connection Error"), e)
        except BaseException as e:
            self.add_error(ServiceUnavailable("Unknown error"), e)
        else:
            logger.debug("Connection established. Redis is healthy.")
