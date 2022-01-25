import logging
import re
from timeit import default_timer as timer

from django.utils.translation import gettext_lazy as _  # noqa: N812
from prometheus_client import REGISTRY, Gauge, Metric

from health_check.conf import HEALTH_CHECK
from health_check.exceptions import (
    BadPrometheusMetricType, HealthCheckException
)

logger = logging.getLogger('health-check')


class BaseHealthCheckBackend:
    critical_service = True
    """
    Define if service is critical to the operation of the site.

    If set to ``True`` service failures return 500 response code on the
    health check endpoint.
    """

    def __init__(self):
        self.errors = []
        self.use_prometheus = HEALTH_CHECK['USE_PROMETHEUS']

    @property
    def class_name_to_snake_case(self):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', self.__class__.__name__).lower()

    @property
    def prometheus_status_metric_name(self) -> str:
        return f"{self.class_name_to_snake_case}_status"

    @property
    def prometheus_status_metric(self) -> Gauge:
        return self.get_prometheus_metric(Gauge, self.prometheus_status_metric_name)

    def get_prometheus_metric(self, metric_type: type, name, description: str = None):
        if issubclass(metric_type, Metric):
            raise BadPrometheusMetricType(f"Metric type '{metric_type}' isn't subclass of prometheus_client.Metric")

        name = f"{HEALTH_CHECK['PROMETHEUS_METRIC_NAMESPACE']}_{name}"
        description = description or f"Check status of {self.identifier()}"

        if name in REGISTRY._get_names(REGISTRY):
            return REGISTRY._names_to_collectors[name]

        return metric_type(name, description)

    def check_status(self):
        raise NotImplementedError

    def run_check(self, external_errors=None):
        start = timer()
        self.errors = external_errors or []
        try:
            self.check_status()
        except HealthCheckException as e:
            self.add_error(e, e)
        except BaseException:
            logger.exception("Unexpected Error!")
            raise
        finally:
            self.time_taken = timer() - start
            if self.use_prometheus:
                self.prometheus_status_metric.set(0 if len(self.errors) else 1)

    def add_error(self, error, cause=None):
        if isinstance(error, HealthCheckException):
            pass
        elif isinstance(error, str):
            msg = error
            error = HealthCheckException(msg)
        else:
            msg = _("unknown error")
            error = HealthCheckException(msg)

        if HEALTH_CHECK['VERBOSE']:
            if isinstance(cause, BaseException):
                logger.exception(str(error))
            else:
                logger.error(str(error))

        self.errors.append(error)

    def pretty_status(self):
        if self.errors:
            return "; ".join(str(e) for e in self.errors)
        return _('working')

    @property
    def status(self):
        return int(not self.errors)

    def identifier(self):
        return self.__class__.__name__


class CommonHealth(BaseHealthCheckBackend):

    def check_status(self):
        pass
