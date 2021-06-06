import logging
import requests

from requests.exceptions import Timeout

from django.conf import settings

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)


class HTTPPingHealthCheck(BaseHealthCheckBackend):
    """Health check using http requests """


    def check_status(self):
        """Check http conections for all urls in settings.HTTP_ENDPOINTS_HEALTH_CHECK"""

        http_endpoints = getattr(settings, "HTTP_ENDPOINTS_HEALTH_CHECK", [])
        timeout = getattr(settings, "HTTP_TIMEOUT_HEALTH_CHECK", 1)

        logger.debug("Got %s as the http_endpoints. ", http_endpoints)

        for http_endpoint in http_endpoints:
            
            try:
                response = requests.get(http_endpoint, timeout=timeout)

            except Timeout as e:
                self.add_error(ServiceUnavailable(f"Timeout conecting to {http_endpoint}"), e)
                return

            except Exception as e:
                self.add_error(ServiceUnavailable(f"Unexpected error conecting to {http_endpoint}"), e)
                return     
            
            if response.status_code >= 300:
                self.add_error(ServiceUnavailable(f"Invalid response status code in {http_endpoint}"))
                return

            logger.debug(f"{http_endpoint} endpoint is healthy.")
        
        logger.debug("All endpoints are healthy.")