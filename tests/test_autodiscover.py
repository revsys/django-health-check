# -*- coding: utf-8 -*-
from django.conf import settings

from health_check.plugins import plugin_dir


class TestAutoDiscover(object):
    def test_autodiscover(self):
        health_check_plugins = list(filter(
            lambda x: 'health_check_' in x,
            settings.INSTALLED_APPS
        ))
        assert len(plugin_dir._registry) == len(health_check_plugins)
