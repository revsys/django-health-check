import json

from django.conf import settings

from health_check.backends import BaseHealthCheckBackend
from health_check.plugins import plugin_dir

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


class TestMainView:
    url = reverse('health_check_home')

    def test_success(self, client):
        response = client.get(self.url)
        assert response.status_code == 200, response.content.decode('utf-8')

    def test_error(self, client):
        class MyBackend(BaseHealthCheckBackend):
            def run_check(self):
                self.add_error('Super Fail!')

        plugin_dir.reset()
        plugin_dir.register(MyBackend)
        response = client.get(self.url)
        assert response.status_code == 500, response.content.decode('utf-8')
        assert b'Super Fail!' in response.content

    def test_success_json(self, client):
        class JSONSuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        plugin_dir.reset()
        plugin_dir.register(JSONSuccessBackend)
        response = client.get(self.url, HTTP_ACCEPT='application/json')
        assert response.status_code == 200, response.content.decode('utf-8')
        assert json.loads(response.content.decode('utf-8')) == \
            {JSONSuccessBackend().identifier(): JSONSuccessBackend().pretty_status()}

    def test_error_json(self, client):
        class JSONErrorBackend(BaseHealthCheckBackend):
            def run_check(self):
                self.add_error('JSON Error')

        plugin_dir.reset()
        plugin_dir.register(JSONErrorBackend)
        response = client.get(self.url, HTTP_ACCEPT='application/json')
        assert response.status_code == 500, response.content.decode('utf-8')
        assert 'JSON Error' in json.loads(response.content.decode('utf-8'))[JSONErrorBackend().identifier()]

    def test_success_json_verbose(self, client):
        settings.HEALTH_CHECK = {
            "HEALTHCHECK_JSON_STATUS": True
        }

        class JSONSuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                self.time_taken = 2.1234567

        plugin_dir.reset()
        plugin_dir.register(JSONSuccessBackend)
        response = client.get(self.url, HTTP_ACCEPT='application/json')
        assert response.status_code == 200, response.content.decode('utf-8')
        assert json.loads(response.content.decode('utf-8')) == \
            {JSONSuccessBackend().identifier(): {"status": JSONSuccessBackend().pretty_status(), "took": 2.1235}}
