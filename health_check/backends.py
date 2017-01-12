# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _

from health_check.exceptions import HealthCheckException

logger = logging.getLogger('health-check')


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
            pass
        elif isinstance(error, text_type):
            msg = error
            error = HealthCheckException(msg)
        else:
            msg = _("unknown error")
            error = HealthCheckException(msg)
        if isinstance(cause, BaseException):
            logger.exception(text_type(error))
        else:
            logger.error(text_type(error))
        self.errors.append(error)

    def pretty_status(self):
        if self.errors:
            return "\n".join(str(e) for e in self.errors)
        return _('working')

    @property
    def status(self):
        return int(not self.errors)

    def identifier(self):
        return self.__class__.__name__
