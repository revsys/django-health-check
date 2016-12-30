# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

logger = logging.getLogger('health-check')


class HealthCheckStatusType(object):
    unavailable = 0
    working = 1
    unexpected_result = 2


@python_2_unicode_compatible
class HealthCheckException(Exception):
    type = _("unknown error")

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "%s: %s" % (self.type, self.message)


class ServiceUnavailable(HealthCheckException):
    type = _("unavailable")


class ServiceReturnedUnexpectedResult(HealthCheckException):
    type = _("unexpected result")


class BaseHealthCheckBackend(object):

    def __init__(self):
        self.errors = []

    def check_status(self):
        raise NotImplementedError

    def run_check(self):
        self.errors = []
        try:
            self.check_status()
        except HealthCheckException as e:
            self.add_error(e, e)
        except BaseException:
            logger.exception("Unexpected Error!")
            raise

    def add_error(self, error, cause=None):
        if isinstance(error, HealthCheckException):
            msg = error.message
        elif isinstance(error, text_type):
            msg = error
            error = HealthCheckException(msg)
        else:
            msg = _("unknown error")
            error = HealthCheckException(msg)
        if isinstance(cause, BaseException):
            logger.exception(msg)
        else:
            logger.error(msg)
        self.errors.append(error)

    def pretty_status(self):
        if self.errors:
            return "/n".join(str(e) for e in self.errors)
        return _('working')

    @property
    def status(self):
        return int(not self.errors)

    @classmethod
    def identifier(cls):
        return cls.__name__
