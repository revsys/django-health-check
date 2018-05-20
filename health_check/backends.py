import logging
from timeit import default_timer as timer

from django.utils.translation import ugettext_lazy as _

from health_check.exceptions import HealthCheckException

logger = logging.getLogger('health-check')


class BaseHealthCheckBackend:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.critical = getattr(self, 'critical', True)
        self.description = getattr(self, 'description', '')

    def check_status(self):
        raise NotImplementedError

    def run_check(self):
        start = timer()
        self.errors = []
        try:
            self.check_status()
        except HealthCheckException as e:
            self.add_error(e, e)
        except BaseException:
            logger.exception("Unexpected Error!")
            raise
        finally:
            self.time_taken = timer() - start

    def _get_error_type(self, error):
        if isinstance(error, HealthCheckException):
            pass
        elif isinstance(error, str):
            msg = error
            error = HealthCheckException(msg)
        else:
            msg = _("unknown error")
            error = HealthCheckException(msg)
        return error

    def add_error(self, error, cause=None):
        error = self._get_error_type(error)

        if isinstance(cause, BaseException):
            logger.exception(str(error))
        else:
            logger.error(str(error))
        self.errors.append(error)

    def add_warning(self, warning, cause=None):
        warning = self._get_error_type(warning)

        if isinstance(cause, BaseException):
            logger.warning(str(warning))
        else:
            logger.warning(str(warning))
        self.warnings.append(warning)

    def pretty_status(self, hide_uncritical=False):
        if not hide_uncritical and (self.errors or self.warnings):
            return "\n".join(str(e) for e in (self.errors + self.warnings))
        return _('working')

    @property
    def status(self):
        return int(not self.errors)

    def identifier(self):
        return self.__class__.__name__
