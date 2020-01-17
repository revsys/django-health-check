from io import StringIO

import pytest
from django.core.management import call_command

from health_check.backends import BaseHealthCheckBackend
from health_check.plugins import plugin_dir


class FailPlugin(BaseHealthCheckBackend):
    def check_status(self):
        self.add_error('Oops')


class OkPlugin(BaseHealthCheckBackend):
    def check_status(self):
        pass


class TestCommand:
    @pytest.yield_fixture(autouse=True)
    def setup(self):
        plugin_dir.reset()
        plugin_dir.register(FailPlugin)
        plugin_dir.register(OkPlugin)
        yield
        plugin_dir.reset()

    def test_command(self):
        stdout = StringIO()
        with pytest.raises(SystemExit):
            call_command("health_check", stdout=stdout)
        stdout.seek(0)
        assert stdout.read() == (
            "FailPlugin               ... unknown error: Oops\n"
            "OkPlugin                 ... working\n"
        )
