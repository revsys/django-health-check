# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from logging import getLogger

from django.utils.translation import ugettext_lazy as _


class HealthCheckStatusType(object):
    unavailable = 0
    working = 1
    unexpected_result = 2

HEALTH_CHECK_STATUS_TYPE_TRANSLATOR = {
    0: _("unavailable"),
    1: _("working"),
    2: _("unexpected result"),
}


class HealthCheckException(Exception):
    pass


class ServiceUnavailable(HealthCheckException):
    message = HEALTH_CHECK_STATUS_TYPE_TRANSLATOR[0]
    code = 0


class ServiceReturnedUnexpectedResult(HealthCheckException):
    message = HEALTH_CHECK_STATUS_TYPE_TRANSLATOR[2]
    code = 2


class BaseHealthCheckBackend(object):

    def check_status(self):
        return None

    @property
    def status(self):
        if not getattr(self, "_status", False):
            try:
                setattr(self, "_status", self.check_status())
            except (ServiceUnavailable, ServiceReturnedUnexpectedResult) as e:
                setattr(self, "_status", e.code)

        return self._status

    def get_logger(self, logger):
        if logger is not None:
            return logger
        if hasattr(self, "logger"):
            return self.logger
        return getLogger(__name__)

    def error(self, exception_class, message, logger):
        self.get_logger(logger).exception(message)
        raise exception_class(message)

    def unexpected(self, message, logger=None):
        self.error(ServiceReturnedUnexpectedResult, message, logger)

    def unavailable(self, message, logger=None):
        self.error(ServiceUnavailable, message, logger)

    def pretty_status(self):
        return "%s" % (HEALTH_CHECK_STATUS_TYPE_TRANSLATOR[self.status])

    @classmethod
    def identifier(cls):
        return cls.__name__
