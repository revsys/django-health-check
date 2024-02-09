from health_check.backends import BaseHealthCheckBackend
from health_check.mixins import CheckMixin


class Checker(CheckMixin):
    pass


class PrometheusChecker(BaseHealthCheckBackend):
    def check_status(self):
        pass

    def check_plugins(self):
        self.errors = []
        checker = Checker()

        try:
            checker.run_check()
        except Exception as err:
            self.add_error(err)

        return checker.plugins
