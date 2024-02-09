from unittest import mock

import pytest
from prometheus_client.core import CollectorRegistry

from health_check.backends import BaseHealthCheckBackend
from health_check.contrib.prometheus.collector import DjangoHealthCheckCollector
from health_check.exceptions import HealthCheckException
from health_check.mixins import CheckMixin
from health_check.plugins import plugin_dir


class FakePlugin(BaseHealthCheckBackend):
    error = None

    def check_status(self):
        if self.error:
            raise self.error


class TestDjangoHealthCheckCollector:
    @pytest.fixture()
    def plugin(self):
        plugin_dir.reset()
        plugin_dir.register(FakePlugin)
        yield FakePlugin
        plugin_dir.reset()

    @pytest.fixture()
    def collector(self):
        return DjangoHealthCheckCollector()

    def test_register_to(self, collector):
        registry = CollectorRegistry(auto_describe=True)
        collector.register_to(registry)

        with mock.patch.object(collector, "collect") as collect:
            list(registry.collect())

            collect.assert_called_once()

    @pytest.mark.parametrize(
        "error, critical_service, errors",
        [
            (None, True, 0),
            (None, False, 0),
            (HealthCheckException("test"), True, 1),
            (HealthCheckException("test"), False, 1),
            (HealthCheckException("test"), True, 1),
            (HealthCheckException("test"), False, 1),
        ],
    )
    def test_collect(self, collector, plugin, error, critical_service, errors):
        plugin.error = error
        plugin.critical_service = critical_service

        metric_families = list(collector.collect())
        assert metric_families

        for metric_family in metric_families:
            sample = metric_family.samples[0]

            assert sample.labels["identifier"] == "FakePlugin"

            if critical_service:
                assert sample.labels["kind"] == "critical_service"
            else:
                assert sample.labels["kind"] == "normal"

            if sample.name == "django_health_check_errors":
                assert sample.value == errors

            elif sample.name == "django_health_check_duration_seconds":
                assert sample.value is not None
