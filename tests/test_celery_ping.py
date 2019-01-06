import pytest

from health_check.contrib.celery_ping.backends import CeleryPingHealthCheck


class TestCeleryWorkersHealthCheck:
    health_check_class = CeleryPingHealthCheck
    CELERY_HEALTH_CHECK_MODULE = \
        'health_check.contrib.celery_ping.backends.app.control.ping'

    def test_check_status_doesnt_add_errors_when_ping_successfull(
            self, mocker):
        mocker.patch(
            self.CELERY_HEALTH_CHECK_MODULE,
            return_value=[{'celery@4cc150a7b49b': {'ok': 'pong'}}])

        health_check = self.health_check_class()
        health_check.check_status()

        assert len(health_check.errors) == 0

    @pytest.mark.parametrize('exception_to_raise', [
        IOError,
        TimeoutError,
    ])
    def test_check_status_add_error_when_io_error_raised_from_ping(
            self, mocker, exception_to_raise):
        mocker.patch(
            self.CELERY_HEALTH_CHECK_MODULE,
            side_effect=exception_to_raise)

        health_check = self.health_check_class()
        health_check.check_status()

        assert len(health_check.errors) == 1
        assert 'ioerror' in health_check.errors[0].message.lower()

    @pytest.mark.parametrize('exception_to_raise', [
        ValueError,
        SystemError,
        IndexError,
        MemoryError,
    ])
    def test_check_status_add_error_when_any_exception_raised_from_ping(
            self, mocker, exception_to_raise):
        mocker.patch(
            self.CELERY_HEALTH_CHECK_MODULE,
            side_effect=exception_to_raise)

        health_check = self.health_check_class()
        health_check.check_status()

        assert len(health_check.errors) == 1
        assert health_check.errors[0].message.lower() == 'unknown error'

    @pytest.mark.parametrize('ping_result', [
        None,
        list()
    ])
    def test_check_status_add_error_when_ping_result_failed(
            self, mocker, ping_result):
        mocker.patch(
            self.CELERY_HEALTH_CHECK_MODULE,
            return_value=ping_result)

        health_check = self.health_check_class()
        health_check.check_status()

        assert len(health_check.errors) == 1
        assert 'workers unavailable' in health_check.errors[0].message.lower()
