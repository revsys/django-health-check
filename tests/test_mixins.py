import pytest

from health_check.backends import BaseHealthCheckBackend
from health_check.mixins import CheckMixin
from health_check.plugins import plugin_dir


class FailPlugin(BaseHealthCheckBackend):
    def check_status(self):
        self.add_error('Oops')


class OkPlugin(BaseHealthCheckBackend):
    def check_status(self):
        pass


class Checker(CheckMixin):
    pass


class TestCheckMixin:
    @pytest.yield_fixture(autouse=True)
    def setup(self):
        plugin_dir.reset()
        plugin_dir.register(FailPlugin)
        plugin_dir.register(OkPlugin)
        yield
        plugin_dir.reset()

    def test_plugins(self):
        assert len(Checker().plugins) == 2

    def test_errors(self):
        assert len(Checker().errors) == 1

    def test_run_check(self):
        assert len(Checker().run_check()) == 1
