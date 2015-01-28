# -*- coding: utf-8 -*-
import pytest
from health_check.plugins import plugin_dir, AlreadyRegistered, NotRegistered
from health_check.backends.base import BaseHealthCheckBackend


class FakePlugin(BaseHealthCheckBackend):

    def check_status(self):
        pass


class Plugin(BaseHealthCheckBackend):

    def check_status(self):
        pass


class TestPlugin(object):

    def setup(self):
        plugin_dir.register(FakePlugin)

    def teardown(self):
        plugin_dir.unregister([FakePlugin])

    def test_register_plugin(self):
        assert len(plugin_dir._registry) == 2

    def test_should_raise_exception_when_registry_a_registrated_plugin(self):

        with pytest.raises(AlreadyRegistered):
            plugin_dir.register(FakePlugin)

        assert len(plugin_dir._registry) == 2

    def test_should_raise_exception_when_unresgistry_plugin_not_registred(self):
        fake = Plugin()
        fake.__name__ = 'Fake'
        with pytest.raises(NotRegistered):
            plugin_dir.unregister(fake)

        assert len(plugin_dir._registry) == 2
