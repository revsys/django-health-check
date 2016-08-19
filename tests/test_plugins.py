# -*- coding: utf-8 -*-
from health_check.backends.base import BaseHealthCheckBackend
from health_check.plugins import AlreadyRegistered, NotRegistered, plugin_dir
from django.test import TestCase


class FakePlugin(BaseHealthCheckBackend):
    def check_status(self):
        pass


class Plugin(BaseHealthCheckBackend):
    def check_status(self):
        pass


class TestPlugin(TestCase):
    def setUp(self):
        plugin_dir._registry = {}
        plugin_dir.register(FakePlugin)

    def tearDown(self):
        plugin_dir._registry = {}

    def test_register_plugin(self):
        self.assertEqual(len(plugin_dir._registry), 1)

    def test_already_registered_exception(self):
        with self.assertRaises(AlreadyRegistered):
            plugin_dir.register(FakePlugin)

        self.assertEqual(len(plugin_dir._registry), 1)

    def test_not_registered_exception(self):
        fake = Plugin()
        fake.__name__ = 'Fake'
        with self.assertRaises(NotRegistered):
            plugin_dir.unregister(fake)

        self.assertEqual(len(plugin_dir._registry), 1)
