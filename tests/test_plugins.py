import pytest

from health_check.backends import BaseHealthCheckBackend
from health_check.plugins import plugin_dir


class FakePlugin(BaseHealthCheckBackend):
    def check_status(self):
        pass


class Plugin(BaseHealthCheckBackend):
    def check_status(self):
        pass


class TestPlugin:
    @pytest.yield_fixture(autouse=True)
    def setup(self):
        plugin_dir.reset()
        plugin_dir.register(FakePlugin)
        yield
        plugin_dir.reset()

    def test_register_plugin(self):
        assert len(plugin_dir._registry) == 1
