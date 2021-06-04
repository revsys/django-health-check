from django.conf import settings
from django.test import TestCase
from health_check.contrib.http_ping.backends import HTTPPingHealthCheck


class TestHTTPPingHealthCheck(TestCase):
    """Test Http Ping health check."""


    def test_connection_ok(self):

        settings.HTTP_ENDPOINTS_HEALTH_CHECK = ["https://github.com"]

        # instantiates the class
        backend = HTTPPingHealthCheck()

        # invokes the method check_status()
        backend.check_status()
        
        self.assertFalse(backend.errors)

    

    def test_connection_timeout(self):

        settings.HTTP_ENDPOINTS_HEALTH_CHECK = ["https://github.com"]
        settings.HTTP_TIMEOUT_HEALTH_CHECK = 0.0001


        # instantiates the class
        backend = HTTPPingHealthCheck()

        # invokes the method check_status()
        backend.check_status()
        
        self.assertTrue(backend.errors)


    def test_connection_fail(self):

        settings.HTTP_ENDPOINTS_HEALTH_CHECK = ["http://error.bad"]


        # instantiates the class
        backend = HTTPPingHealthCheck()

        # invokes the method check_status()
        backend.check_status()
        
        self.assertTrue(backend.errors)


