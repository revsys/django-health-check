import dataclasses
import logging
import warnings
from timeit import default_timer as timer

from django.utils.translation import gettext_lazy as _  # noqa: N812

from health_check.exceptions import HealthCheckException

logger = logging.getLogger("health-check")


@dataclasses.dataclass()
class BaseHealthCheckBackend:
    """
    Base class for all health check backends.

    To create your own health check backend, subclass this class
    and implement the ``check_status`` method.
    """

    critical_service: bool = dataclasses.field(init=False, default=True, repr=False)
    errors: list[HealthCheckException] = dataclasses.field(init=False, default_factory=list)

    def check_status(self):
        """
        Execute the health check logic.

        This method should be overridden by subclasses to implement
        specific health check logic. If the check fails, it should
        call `self.add_error` with an appropriate error message or
        raise a `HealthCheckException`.

        Raises:
            HealthCheckException: If the health check fails.
            ServiceWarning: If the health check encounters a warning condition.

        """
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

    def add_error(self, error, cause=None):
        if isinstance(error, HealthCheckException):
            pass
        elif isinstance(error, str):
            msg = error
            error = HealthCheckException(msg)
        else:
            msg = _("unknown error")
            error = HealthCheckException(msg)
        if isinstance(cause, BaseException):
            logger.exception(str(error))
        else:
            logger.error(str(error))
        self.errors.append(error)

    def pretty_status(self):
        if self.errors:
            return "\n".join(str(e) for e in self.errors)
        return _("working")

    @property
    def status(self):
        return int(not self.errors)

    def identifier(self):
        return self.__class__.__name__

    def __repr__(self):
        if hasattr(self, "identifier"):
            warnings.warn("identifier method is deprecated, use __repr__ instead", DeprecationWarning)
            return self.identifier()

        return super().__repr__()
