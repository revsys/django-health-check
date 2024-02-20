from io import StringIO

import pytest
from django.core.management import call_command

from health_check.backends import BaseHealthCheckBackend
from health_check.conf import HEALTH_CHECK
from health_check.plugins import plugin_dir


class FailPlugin(BaseHealthCheckBackend):
    def check_status(self):
        self.add_error("Oops")


class OkPlugin(BaseHealthCheckBackend):
    def check_status(self):
        pass


class TestCommand:
    @pytest.fixture(autouse=True)
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

    def test_command_with_subset(self):
        SUBSET_NAME_1 = "subset-1"
        SUBSET_NAME_2 = "subset-2"
        HEALTH_CHECK["SUBSETS"] = {
            SUBSET_NAME_1: ["OkPlugin"],
            SUBSET_NAME_2: ["OkPlugin", "FailPlugin"],
        }

        stdout = StringIO()
        call_command("health_check", f"--subset={SUBSET_NAME_1}", stdout=stdout)
        stdout.seek(0)
        assert stdout.read() == ("OkPlugin                 ... working\n")

    def test_command_with_failed_check_subset(self):
        SUBSET_NAME = "subset-2"
        HEALTH_CHECK["SUBSETS"] = {SUBSET_NAME: ["OkPlugin", "FailPlugin"]}

        stdout = StringIO()
        with pytest.raises(SystemExit):
            call_command("health_check", f"--subset={SUBSET_NAME}", stdout=stdout)
        stdout.seek(0)
        assert stdout.read() == (
            "FailPlugin               ... unknown error: Oops\n"
            "OkPlugin                 ... working\n"
        )

    def test_command_with_non_existence_subset(self):
        SUBSET_NAME = "subset-2"
        NON_EXISTENCE_SUBSET_NAME = "abcdef12"
        HEALTH_CHECK["SUBSETS"] = {SUBSET_NAME: ["OkPlugin"]}

        stdout = StringIO()
        with pytest.raises(SystemExit):
            call_command(
                "health_check", f"--subset={NON_EXISTENCE_SUBSET_NAME}", stdout=stdout
            )
        stdout.seek(0)
        assert stdout.read() == (
            f"Subset: '{NON_EXISTENCE_SUBSET_NAME}' does not exist.\n"
        )
