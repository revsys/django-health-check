import logging

from django.conf import settings
from redis import from_url, exceptions

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)


class RedisHealthCheck(BaseHealthCheckBackend):
    """Health check for Redis."""

    def check_status(self):
        """Check Redis service by opening and closing a connection."""
        logger.debug("Checking for a redis_url in django settings...")

        redis_url = getattr(settings, "REDIS_URL", None)

        logger.debug("Got %s as the redis_url. Connecting to redis...", redis_url)

        logger.debug("Attempting to connect to redis...")
        try:
            # conn is used as a context to release opened resources later
            with from_url(redis_url) as conn:
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
            logger.info("Connection established. Redis is healthy.")
