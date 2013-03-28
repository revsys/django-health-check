# -*- coding: utf-8 -*-
from django.db.models.options import get_verbose_name
from health_check.backends.base import HealthCheckStatusType, BaseHealthCheckBackend
from health_check.plugins import plugin_dir


class BaseHealthCheck(BaseHealthCheckBackend):
    def check_status(self):
        try:
            self._wrapped()
        except HealthCheckFailed:
            return HealthCheckStatusType.unexpected_result
        except HealthCheckUnavailable:
            return HealthCheckStatusType.unavailable
        except:
            return HealthCheckStatusType.unexpected_result
        return HealthCheckStatusType.working

class HealthCheckFailed(Exception):
    pass

class HealthCheckUnavailable(Exception):
    pass


def healtcheck(func_or_name):
    """
    Usage:

        @healthcheck("My Check")
        def my_check():
            if something_is_not_okay():
                raise HealthCheckFailed()

        @healthcheck
        def other_check():
            if something_is_not_available():
                raise HealthCHeckUnavailable()
    """
    def inner(func):
        cls = type(func.__name__, (BaseHealthCheck,), {'_wrapped': func})
        cls.identifier = name
        plugin_dir.register(cls)
        return func
    if callable(func_or_name):
        name = get_verbose_name(func_or_name.__name__).replace('_', ' ')
        return inner(func_or_name)
    else:
        name = func_or_name
        return inner
