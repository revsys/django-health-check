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

HEALTH_CHECK_JSON_STATUS_TYPE = {
    0: "DOWN",
    1: "OK",
    2: "WARNING",
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

    def json_status(self):
        return HEALTH_CHECK_JSON_STATUS_TYPE[self.status]

    def pretty_status(self):
        return u"%s" % (HEALTH_CHECK_STATUS_TYPE_TRANSLATOR[self.status])

    @classmethod
    def identifier(cls):
        return cls.__name__
