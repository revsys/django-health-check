# -*- coding: utf-8 -*-
import pytest

from health_check.backends.base import BaseHealthCheckBackend


class TestBaseHealthCheckBackend(object):

    def test_run_check(self):
        with pytest.raises(NotImplementedError):
            BaseHealthCheckBackend().run_check()
