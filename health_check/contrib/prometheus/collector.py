from prometheus_client.core import GaugeMetricFamily

from health_check.mixins import CheckMixin


class Checker(CheckMixin):
    pass


class DjangoHealthCheckCollector:
    def collect(self):
        django_health_check_errors = GaugeMetricFamily(
            "django_health_check_errors",
            "The errors returned by the health checks",
            labels=["plugin", "critical_service"],
        )
        django_health_check_duration_seconds = GaugeMetricFamily(
            "django_health_check_duration_seconds",
            "The seconds taken by the health checks",
            labels=["plugin", "critical_service"],
        )

        checker = Checker()

        try:
            checker.run_check()
        except Exception:
            return

        for plugin in checker.plugins:
            labels = [str(plugin.identifier()), "1" if plugin.critical_service else "0"]

            django_health_check_errors.add_metric(labels, len(plugin.errors))
            django_health_check_duration_seconds.add_metric(labels, plugin.time_taken)

        yield django_health_check_errors
        yield django_health_check_duration_seconds

    def register_to(self, registry):
        registry.register(self)
