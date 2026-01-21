import logging
import importlib

from django.conf import settings

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)


try:
    kafka_module = importlib.import_module("kafka")
except ImportError:
    kafka_module = None

if not kafka_module:
    raise ImportError(
        "No kafka-python or kafka-python-ng library found. Please install one of them."
    )

KafkaAdminClient = getattr(kafka_module, "KafkaAdminClient", None)
KafkaError = getattr(importlib.import_module("kafka.errors"), "KafkaError", None)

if not KafkaAdminClient or not KafkaError:
    raise ImportError(
        "KafkaAdminClient or KafkaError not available. Please check your installations."
    )


class KafkaHealthCheck(BaseHealthCheckBackend):
    """Health check for Kafka."""

    namespace = None

    def check_status(self):
        """Check Kafka service by opening and closing a broker channel."""
        logger.debug("Checking for a KAFKA_URL on django settings...")

        bootstrap_servers = getattr(settings, "KAFKA_URL", None)

        logger.debug(
            "Got %s as the kafka_url. Connecting to kafka...", bootstrap_servers
        )

        logger.debug("Attempting to connect to kafka...")
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=bootstrap_servers,
                request_timeout_ms=3000,  # 3 secondes max
                api_version_auto_timeout_ms=1000,
            )
            # Ping léger : on liste les topics (lecture metadata)
            admin_client.list_topics()
        except KafkaError as e:
            self.add_error(ServiceUnavailable("Unknown error"), e)
        else:
            logger.debug("Connection established. Kafka is healthy.")
