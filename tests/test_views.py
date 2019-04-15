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
    url = reverse('health_check:health_check_home')

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
        assert response['content-type'] == 'text/html; charset=utf-8'
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
        assert response['content-type'] == 'text/html; charset=utf-8'
        assert b'Super Fail!' in response.content

    def test_success_prefer_html_request_json(self, client):
        class MySuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        HEALTH_CHECK['PREFERRED_FORMAT'] = 'html'

        plugin_dir.reset()
        plugin_dir.register(MySuccessBackend)
        response = client.get(self.url, HTTP_ACCEPT='application/json')
        assert response.status_code == 200, response.content.decode('utf-8')
        assert response['content-type'] == 'application/json'
        json_response = json.loads(response.content.decode('utf-8'))
        assert 'working' == json_response[MySuccessBackend().identifier()]

    def test_success_prefer_json_request_html(self, client):
        class MySuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        HEALTH_CHECK['PREFERRED_FORMAT'] = 'json'

        plugin_dir.reset()
        plugin_dir.register(MySuccessBackend)
        response = client.get(self.url, HTTP_ACCEPT='text/html')
        assert response.status_code == 200, response.content.decode('utf-8')
        assert response['content-type'] == 'text/html; charset=utf-8'

    def test_success_prefer_html_request_neither(self, client):
        class MySuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        HEALTH_CHECK['PREFERRED_FORMAT'] = 'html'

        plugin_dir.reset()
        plugin_dir.register(MySuccessBackend)
        response = client.get(self.url)
        assert response.status_code == 200, response.content.decode('utf-8')
        assert response['content-type'] == 'text/html; charset=utf-8'

    def test_success_prefer_json_request_neither(self, client):
        class MySuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        HEALTH_CHECK['PREFERRED_FORMAT'] = 'json'

        plugin_dir.reset()
        plugin_dir.register(MySuccessBackend)
        response = client.get(self.url)
        assert response.status_code == 200, response.content.decode('utf-8')
        assert response['content-type'] == 'application/json'
        json_response = json.loads(response.content.decode('utf-8'))
        assert 'working' == json_response[MySuccessBackend().identifier()]

    def test_success_prefer_html_request_either(self, client):
        class MySuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        HEALTH_CHECK['PREFERRED_FORMAT'] = 'html'

        plugin_dir.reset()
        plugin_dir.register(MySuccessBackend)
        response = client.get(self.url, HTTP_ACCEPT='text/html, application/json')
        assert response.status_code == 200, response.content.decode('utf-8')
        assert response['content-type'] == 'text/html; charset=utf-8'

    def test_success_prefer_json_request_either(self, client):
        class MySuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        HEALTH_CHECK['PREFERRED_FORMAT'] = 'json'

        plugin_dir.reset()
        plugin_dir.register(MySuccessBackend)
        response = client.get(self.url, HTTP_ACCEPT='text/html, application/json')
        assert response.status_code == 200, response.content.decode('utf-8')
        assert response['content-type'] == 'application/json'
        json_response = json.loads(response.content.decode('utf-8'))
        assert 'working' == json_response[MySuccessBackend().identifier()]

    def test_error_prefer_html_request_json(self, client):
        class MyErrorBackend(BaseHealthCheckBackend):
            def run_check(self):
                self.add_error('Some error')

        HEALTH_CHECK['PREFERRED_FORMAT'] = 'html'

        plugin_dir.reset()
        plugin_dir.register(MyErrorBackend)
        response = client.get(self.url, HTTP_ACCEPT='application/json')
        assert response.status_code == 500, response.content.decode('utf-8')
        assert response['content-type'] == 'application/json'

    def test_error_prefer_json_request_html(self, client):
        class MyErrorBackend(BaseHealthCheckBackend):
            def run_check(self):
                self.add_error('Some error')

        HEALTH_CHECK['PREFERRED_FORMAT'] = 'json'

        plugin_dir.reset()
        plugin_dir.register(MyErrorBackend)
        response = client.get(self.url, HTTP_ACCEPT='text/html')
        assert response.status_code == 500, response.content.decode('utf-8')
        assert response['content-type'] == 'text/html; charset=utf-8'
        assert 'Some error' in response.content.decode('utf-8')

    def test_error_prefer_html_request_neither(self, client):
        class MyErrorBackend(BaseHealthCheckBackend):
            def run_check(self):
                self.add_error('Some error')

        HEALTH_CHECK['PREFERRED_FORMAT'] = 'html'

        plugin_dir.reset()
        plugin_dir.register(MyErrorBackend)
        response = client.get(self.url)
        assert response.status_code == 500, response.content.decode('utf-8')
        assert response['content-type'] == 'text/html; charset=utf-8'
        assert 'Some error' in response.content.decode('utf-8')

    def test_error_prefer_json_request_neither(self, client):
        class MyErrorBackend(BaseHealthCheckBackend):
            def run_check(self):
                self.add_error('Some error')

        HEALTH_CHECK['PREFERRED_FORMAT'] = 'json'

        plugin_dir.reset()
        plugin_dir.register(MyErrorBackend)
        response = client.get(self.url)
        assert response.status_code == 500, response.content.decode('utf-8')
        assert response['content-type'] == 'application/json'
        json_response = json.loads(response.content.decode('utf-8'))
        assert 'Some error' in json_response[MyErrorBackend().identifier()]

    def test_error_prefer_html_request_either(self, client):
        class MyErrorBackend(BaseHealthCheckBackend):
            def run_check(self):
                self.add_error('Some error')

        HEALTH_CHECK['PREFERRED_FORMAT'] = 'html'

        plugin_dir.reset()
        plugin_dir.register(MyErrorBackend)
        response = client.get(self.url, HTTP_ACCEPT='text/html, application/json')
        assert response.status_code == 500, response.content.decode('utf-8')
        assert response['content-type'] == 'text/html; charset=utf-8'
        assert 'Some error' in response.content.decode('utf-8')

    def test_error_prefer_json_request_either(self, client):
        class MyErrorBackend(BaseHealthCheckBackend):
            def run_check(self):
                self.add_error('Some error')

        HEALTH_CHECK['PREFERRED_FORMAT'] = 'json'

        plugin_dir.reset()
        plugin_dir.register(MyErrorBackend)
        response = client.get(self.url, HTTP_ACCEPT='text/html, application/json')
        assert response.status_code == 500, response.content.decode('utf-8')
        assert response['content-type'] == 'application/json'
        json_response = json.loads(response.content.decode('utf-8'))
        assert 'Some error' in json_response[MyErrorBackend().identifier()]

    def test_success_json(self, client):
        class JSONSuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        plugin_dir.reset()
        plugin_dir.register(JSONSuccessBackend)
        response = client.get(self.url, HTTP_ACCEPT='application/json')
        assert response.status_code == 200, response.content.decode('utf-8')
        assert response['content-type'] == 'application/json'
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
        assert response['content-type'] == 'application/json'
        assert 'JSON Error' in json.loads(response.content.decode('utf-8'))[JSONErrorBackend().identifier()]
