from unittest.mock import patch

import pytest

from health_check.backends import BaseHealthCheckBackend
from health_check.conf import HEALTH_CHECK
from health_check.mixins import CheckMixin
from health_check.plugins import plugin_dir


class FailPlugin(BaseHealthCheckBackend):
    def check_status(self):
        self.add_error("Oops")


class OkPlugin(BaseHealthCheckBackend):
    def check_status(self):
        pass


class Checker(CheckMixin):
    pass


class TestCheckMixin:
    @pytest.fixture(autouse=True)
    def setup(self):
        plugin_dir.reset()
        plugin_dir.register(FailPlugin)
        plugin_dir.register(OkPlugin)
        yield
        plugin_dir.reset()

    @pytest.mark.parametrize("disable_threading", [(True,), (False,)])
    def test_plugins(self, monkeypatch, disable_threading):
        monkeypatch.setitem(HEALTH_CHECK, "DISABLE_THREADING", disable_threading)

        assert len(Checker().plugins) == 2

    @pytest.mark.parametrize("disable_threading", [(True,), (False,)])
    def test_errors(self, monkeypatch, disable_threading):
        monkeypatch.setitem(HEALTH_CHECK, "DISABLE_THREADING", disable_threading)

        assert len(Checker().errors) == 1

    @pytest.mark.parametrize("disable_threading", [(True,), (False,)])
    def test_run_check(self, monkeypatch, disable_threading):
        monkeypatch.setitem(HEALTH_CHECK, "DISABLE_THREADING", disable_threading)

        assert len(Checker().run_check()) == 1

    def test_run_check_threading_enabled(self, monkeypatch):
        """Ensure threading used when not disabled."""

        # Ensure threading is enabled.
        monkeypatch.setitem(HEALTH_CHECK, "DISABLE_THREADING", False)

        # Ensure ThreadPoolExecutor is used
        with patch("health_check.mixins.ThreadPoolExecutor") as tpe:
            Checker().run_check()
            tpe.assert_called()

    def test_run_check_threading_disabled(self, monkeypatch):
        """Ensure threading not used when disabled."""

        # Ensure threading is disabled.
        monkeypatch.setitem(HEALTH_CHECK, "DISABLE_THREADING", True)

        # Ensure ThreadPoolExecutor is not used
        with patch("health_check.mixins.ThreadPoolExecutor") as tpe:
            Checker().run_check()
            tpe.assert_not_called()
