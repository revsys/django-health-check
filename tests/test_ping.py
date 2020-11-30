from django.urls import reverse
from django.test import TestCase


class TestPingHealthCheck(TestCase):
    url = reverse('health_check:health_check_ping')

    def test_check_status_works(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert response.content == b'pong'
