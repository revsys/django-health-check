import logging
from django.conf import settings
from pymongo import MongoClient, errors

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)


class MongoHealthCheck(BaseHealthCheckBackend):
    """Health check for Mongo."""
    mongo_host = getattr(settings, "MONGO_HOST", 'localhost')

    def check_status(self):
        """Check Mongo service connection."""

        logger.debug("Got %s as the mongo host. Connecting to mongo...", self.mongo_host)
        logger.debug("Attempting to connect to mongo...")
        client = MongoClient(host=[self.mongo_host])
        try:
            client.server_info()
        except errors.PyMongoError as e:
            self.add_error(ServiceUnavailable("Unable to connect to Mongo: Connection was refused."), e)
        else:
            logger.debug("Connection established. Mongo is healthy.")
