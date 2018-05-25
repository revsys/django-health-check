import json

from health_check.backends import BaseHealthCheckBackend
from health_check.conf import HEALTH_CHECK
from health_check.exceptions import ServiceWarning
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
            def check_status(self):
                self.add_error('Super Fail!')

        plugin_dir.reset()
        plugin_dir.register(MyBackend)
        response = client.get(self.url)
        assert response.status_code == 500, response.content.decode('utf-8')
        assert b'Super Fail!' in response.content

    def test_warning(self, client):
        class MyBackend(BaseHealthCheckBackend):
            def check_status(self):
                raise ServiceWarning('so so')

        plugin_dir.reset()
        plugin_dir.register(MyBackend)
        response = client.get(self.url)
        assert response.status_code == 500, response.content.decode('utf-8')
        assert b'so so' in response.content, response.content

        HEALTH_CHECK['WARNINGS_AS_ERRORS'] = False

        response = client.get(self.url)
        assert response.status_code == 200, response.content.decode('utf-8')
        assert b'so so' in response.content, response.content

    def test_non_critical(self, client):
        class MyBackend(BaseHealthCheckBackend):
            critical_service = False

            def check_status(self):
                self.add_error('Super Fail!')

        plugin_dir.reset()
        plugin_dir.register(MyBackend)
        response = client.get(self.url)
        assert response.status_code == 200, response.content.decode('utf-8')
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
