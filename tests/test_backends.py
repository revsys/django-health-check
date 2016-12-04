# -*- coding: utf-8 -*-
from health_check.backends.base import BaseHealthCheckBackend


class TestBaseHealthCheckBackend(object):

    def test_status(self):
        assert BaseHealthCheckBackend().status is None
