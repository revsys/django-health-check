from django.apps import AppConfig
from prometheus_client.core import REGISTRY

from health_check.plugins import plugin_dir

from .backends import PrometheusChecker
from .collector import DjangoHealthCheckCollector


class HealthCheckConfig(AppConfig):
    name = "health_check.contrib.prometheus"

    def ready(self):
        collector = DjangoHealthCheckCollector()
        collector.register_to(REGISTRY)

        plugin_dir.register(PrometheusChecker)
