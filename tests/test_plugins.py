# -*- coding: utf-8 -*-
import pytest

from health_check.backends.base import BaseHealthCheckBackend
from health_check.plugins import AlreadyRegistered, NotRegistered, plugin_dir


class FakePlugin(BaseHealthCheckBackend):
    def check_status(self):
        pass


class Plugin(BaseHealthCheckBackend):
    def check_status(self):
        pass


class TestPlugin(object):
    @pytest.yield_fixture(autouse=True)
    def setup(self):
        plugin_dir.reset()
        plugin_dir.register(FakePlugin)
        yield
        plugin_dir.unregister([FakePlugin])

    def test_register_plugin(self):
        assert len(plugin_dir._registry) == 1

    def test_already_registered_exception(self):
        with pytest.raises(AlreadyRegistered):
            plugin_dir.register(FakePlugin)

        assert len(plugin_dir._registry) == 1

    def test_not_registered_exception(self):
        fake = Plugin()
        fake.__name__ = 'Fake'
        with pytest.raises(NotRegistered):
            plugin_dir.unregister(fake)

        assert len(plugin_dir._registry) == 1
