import json
import pytest

from health_check.backends import BaseHealthCheckBackend
from health_check.conf import HEALTH_CHECK
from health_check.exceptions import ServiceWarning
from health_check.plugins import plugin_dir
from health_check.views import MediaType
from rest_framework.test import APIClient

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


class TestMediaType:

    def test_lt(self):
        assert not MediaType('*/*') < MediaType('*/*')
        assert not MediaType('*/*') < MediaType('*/*', 0.9)
        assert MediaType('*/*', 0.9) < MediaType('*/*')

    def test_str(self):
        assert str(MediaType('*/*')) == "*/*; q=1.0"
        assert str(MediaType('image/*', 0.6)) == "image/*; q=0.6"

    def test_repr(self):
        assert repr(MediaType('*/*')) == "MediaType: */*; q=1.0"

    def test_eq(self):
        assert MediaType('*/*') == MediaType('*/*')
        assert MediaType('*/*', 0.9) != MediaType('*/*')

    valid_strings = [
        ('*/*', MediaType('*/*')),
        ('*/*; q=0.9', MediaType('*/*', 0.9)),
        ('*/*; q=0', MediaType('*/*', 0.0)),
        ('*/*; q=0.0', MediaType('*/*', 0.0)),
        ('*/*; q=0.1', MediaType('*/*', 0.1)),
        ('*/*; q=0.12', MediaType('*/*', 0.12)),
        ('*/*; q=0.123', MediaType('*/*', 0.123)),
        ('*/*; q=1.000', MediaType('*/*', 1.0)),
        ('*/*; q=1', MediaType('*/*', 1.0)),
        ('*/*;q=0.9', MediaType('*/*', 0.9)),
        ('*/* ;q=0.9', MediaType('*/*', 0.9)),
        ('*/* ; q=0.9', MediaType('*/*', 0.9)),
        ('*/* ;   q=0.9', MediaType('*/*', 0.9)),
        ('*/*;v=b3', MediaType('*/*')),
        ('*/*; q=0.5; v=b3', MediaType('*/*', 0.5)),
    ]

    @pytest.mark.parametrize("type_arg, expected", valid_strings)
    def test_from_valid_strings(self, type_arg, expected):
        assert MediaType.from_string(type_arg) == expected

    invalid_strings = [
        '*/*;0.9',
        'text/html;z=""',
        'text/html; xxx',
        'text/html;  =a',
    ]

    @pytest.mark.parametrize("type_arg", invalid_strings)
    def test_from_invalid_strings(self, type_arg):
        with pytest.raises(ValueError) as e:
            MediaType.from_string(type_arg)
        expected_error = '"%s" is not a valid media type' % type_arg
        assert expected_error in str(e.value)

    def test_parse_header(self):
        assert list(MediaType.parse_header()) == [
            MediaType('*/*'),
        ]
        assert list(MediaType.parse_header('text/html; q=0.1, application/xhtml+xml; q=0.1 ,application/json')) == [
            MediaType('application/json'),
            MediaType('text/html', 0.1),
            MediaType('application/xhtml+xml', 0.1),
        ]


@pytest.fixture
def api_client():
    return APIClient()


class TestDRFView:
    url = reverse('health_check:health_check_home_v2')

    @classmethod
    def setup_class(cls):
        cls.registry = plugin_dir._registry.copy()
        HEALTH_CHECK['WARNINGS_AS_ERRORS'] = True

    @classmethod
    def teardown_class(cls):
        plugin_dir._registry = cls.registry.copy()
        HEALTH_CHECK['WARNINGS_AS_ERRORS'] = True

    def test_success(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 200, response.content.decode('utf-8')
        assert response['content-type'] == 'text/html; charset=utf-8'

    def test_error(self, api_client):
        class MyBackend(BaseHealthCheckBackend):
            def check_status(self):
                self.add_error('Super Fail!')

        plugin_dir.reset()
        plugin_dir.register(MyBackend)
        response = api_client.get(self.url)
        assert response.status_code == 500, response.content.decode('utf-8')
        assert response['content-type'] == 'text/html; charset=utf-8'
        assert b'Super Fail!' in response.content

    def test_warning(self, api_client):
        class MyBackend(BaseHealthCheckBackend):
            def check_status(self):
                raise ServiceWarning('so so')

        plugin_dir.reset()
        plugin_dir.register(MyBackend)
        response = api_client.get(self.url)
        assert response.status_code == 500, response.content.decode('utf-8')
        assert b'so so' in response.content, response.content

        HEALTH_CHECK['WARNINGS_AS_ERRORS'] = False

        response = api_client.get(self.url)
        assert response.status_code == 200, response.content.decode('utf-8')
        assert response['content-type'] == 'text/html; charset=utf-8'
        assert b'so so' in response.content, response.content

    def test_non_critical(self, api_client):
        class MyBackend(BaseHealthCheckBackend):
            critical_service = False

            def check_status(self):
                self.add_error('Super Fail!')

        plugin_dir.reset()
        plugin_dir.register(MyBackend)
        response = api_client.get(self.url)
        assert response.status_code == 200, response.content.decode('utf-8')
        assert response['content-type'] == 'text/html; charset=utf-8'
        assert b'Super Fail!' in response.content

    def test_success_accept_json(self, api_client):
        class JSONSuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        plugin_dir.reset()
        plugin_dir.register(JSONSuccessBackend)
        response = api_client.get(self.url, HTTP_ACCEPT='application/json')
        assert response['content-type'] == 'application/json'
        assert response.status_code == 200

    def test_success_prefer_json(self, api_client):
        class JSONSuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        plugin_dir.reset()
        plugin_dir.register(JSONSuccessBackend)
        response = api_client.get(self.url, HTTP_ACCEPT='application/json; q=0.8')
        assert response['content-type'] == 'application/json'
        assert response.status_code == 200

    def test_success_accept_xhtml(self, api_client):
        class SuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        plugin_dir.reset()
        plugin_dir.register(SuccessBackend)
        response = api_client.get(self.url, HTTP_ACCEPT='application/xhtml+xml')
        assert response['content-type'] == 'text/html; charset=utf-8'
        assert response.status_code == 406

    def test_success_unsupported_accept(self, api_client):
        class SuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        plugin_dir.reset()
        plugin_dir.register(SuccessBackend)
        response = api_client.get(self.url, HTTP_ACCEPT='application/octet-stream')
        assert response['content-type'] == 'text/html; charset=utf-8'
        assert response.status_code == 406
        assert response.content == b'406 Not Acceptable'

    def test_success_unsupported_and_supported_accept(self, api_client):
        class SuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        plugin_dir.reset()
        plugin_dir.register(SuccessBackend)
        response = api_client.get(self.url, HTTP_ACCEPT='application/octet-stream, application/json; q=0.9')
        assert response['content-type'] == 'application/json'
        assert response.status_code == 200

    def test_success_accept_order(self, api_client):
        class JSONSuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        plugin_dir.reset()
        plugin_dir.register(JSONSuccessBackend)
        response = api_client.get(
            self.url,
            HTTP_ACCEPT='text/html, application/xhtml+xml, application/json; q=0.9, */*; q=0.1'
        )
        assert response['content-type'] == 'text/html; charset=utf-8'
        assert response.status_code == 200

    def test_success_accept_order__reverse(self, api_client):
        class JSONSuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        plugin_dir.reset()
        plugin_dir.register(JSONSuccessBackend)
        response = api_client.get(self.url, HTTP_ACCEPT='text/html; q=0.1, application/xhtml+xml; q=0.1, application/json')
        assert response['content-type'] == 'text/html; charset=utf-8'
        assert response.status_code == 200

    def test_format_no_accept_header(self, api_client):
        class JSONSuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        plugin_dir.reset()
        plugin_dir.register(JSONSuccessBackend)
        response = api_client.get(self.url)
        assert response.status_code == 200, response.content.decode('utf-8')
        assert response['content-type'] == 'text/html; charset=utf-8'

    def test_error_accept_json(self, api_client):
        class JSONErrorBackend(BaseHealthCheckBackend):
            def run_check(self):
                self.add_error('JSON Error')

        plugin_dir.reset()
        plugin_dir.register(JSONErrorBackend)
        response = api_client.get(self.url, HTTP_ACCEPT='application/json')
        assert response.status_code == 500, response.content.decode('utf-8')
        assert response['content-type'] == 'application/json'
        assert 'JSON Error' in json.loads(response.content.decode('utf-8'))["data"][0]["status"]

    def test_success_param_json(self, api_client):
        class JSONSuccessBackend(BaseHealthCheckBackend):
            def run_check(self):
                pass

        plugin_dir.reset()
        plugin_dir.register(JSONSuccessBackend)
        response = api_client.get(self.url, {'format': 'json'})
        assert response.status_code == 200, response.content.decode('utf-8')
        assert response['content-type'] == 'application/json'
        assert json.loads(response.content.decode('utf-8')) == {
            "data": [
                {
                    "name": JSONSuccessBackend().identifier(),
                    "status": JSONSuccessBackend().pretty_status(),
                    "time_taken": None
                }
            ]
        }

    def test_error_param_json(self, api_client):
        class JSONErrorBackend(BaseHealthCheckBackend):
            def run_check(self):
                self.add_error('JSON Error')

        plugin_dir.reset()
        plugin_dir.register(JSONErrorBackend)
        response = api_client.get(self.url, {'format': 'json'})
        assert response.status_code == 500, response.content.decode('utf-8')
        assert response['content-type'] == 'application/json'
        assert 'JSON Error' in json.loads(response.content.decode('utf-8'))["data"][0]["status"]
