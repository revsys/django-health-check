# -*- coding: utf-8 -*-
import health_check.urls
from health_check.plugins import plugin_dir


class TestAutoDiscover(object):

    def test_autodiscover(self):
        assert len(plugin_dir._registry) == 1
