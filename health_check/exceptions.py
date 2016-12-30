from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


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
