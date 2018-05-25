from django.utils.translation import ugettext_lazy as _


class HealthCheckException(Exception):
    message_type = _("unknown error")

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "%s: %s" % (self.message_type, self.message)


class ServiceWarning(HealthCheckException):
    """
    Warning of service misbehavior.

    If the ``HEALTH_CHECK['WARNINGS_AS_ERRORS']`` is set to ``False``,
    these exceptions will not case a 500 status response.
    """

    message_type = _("warning")


class ServiceUnavailable(HealthCheckException):
    message_type = _("unavailable")


class ServiceReturnedUnexpectedResult(HealthCheckException):
    message_type = _("unexpected result")
