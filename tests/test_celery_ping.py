from django.apps import apps

import pytest

from health_check.contrib.celery_ping.apps import HealthCheckConfig
from health_check.contrib.celery_ping.backends import CeleryPingHealthCheck
from mock import patch


class TestCeleryPingHealthCheck:
    health_check_class = CeleryPingHealthCheck
    CELERY_HEALTH_CHECK_MODULE = \
        'health_check.contrib.celery_ping.backends.app.control.ping'

    def test_check_status_doesnt_add_errors_when_ping_successfull(self):
        with patch(self.CELERY_HEALTH_CHECK_MODULE,
                   return_value=[{'celery@4cc150a7b49b': {'ok': 'pong'}}]):
            health_check = self.health_check_class()
            health_check.check_status()

            assert len(health_check.errors) == 0

    @pytest.mark.parametrize('exception_to_raise', [
        IOError,
        TimeoutError,
    ])
    def test_check_status_add_error_when_io_error_raised_from_ping(
            self, exception_to_raise):
        with patch(self.CELERY_HEALTH_CHECK_MODULE,
                   side_effect=exception_to_raise):
            health_check = self.health_check_class()
            health_check.check_status()

            assert len(health_check.errors) == 1
            assert 'ioerror' in health_check.errors[0].message.lower()

    @pytest.mark.parametrize('exception_to_raise', [
        ValueError,
        SystemError,
        IndexError,
        MemoryError
    ])
    def test_check_status_add_error_when_any_exception_raised_from_ping(
            self, exception_to_raise):
        with patch(self.CELERY_HEALTH_CHECK_MODULE,
                   side_effect=exception_to_raise):
            health_check = self.health_check_class()
            health_check.check_status()

            assert len(health_check.errors) == 1
            assert health_check.errors[0].message.lower() == 'unknown error'

    def test_check_status_when_raised_exception_notimplementederror(self):
        msg = 'notimplementederror: make sure celery_result_backend is set'

        with patch(self.CELERY_HEALTH_CHECK_MODULE,
                   side_effect=NotImplementedError):
            health_check = self.health_check_class()
            health_check.check_status()

            assert len(health_check.errors) == 1
            assert health_check.errors[0].message.lower() == msg

    @pytest.mark.parametrize('ping_result', [
        None,
        list()
    ])
    def test_check_status_add_error_when_ping_result_failed(
            self, ping_result):
        with patch(self.CELERY_HEALTH_CHECK_MODULE,
                   return_value=ping_result):
            health_check = self.health_check_class()
            health_check.check_status()

            assert len(health_check.errors) == 1
            assert 'workers unavailable' in health_check.errors[0].message.lower()


class TestCeleryPingHealthCheckApps:

    def test_apps(self):
        assert HealthCheckConfig.name == 'health_check.contrib.celery_ping'

        celery_ping = apps.get_app_config('celery_ping')
        assert celery_ping.name == 'health_check.contrib.celery_ping'
