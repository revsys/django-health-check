# -*- coding: utf-8 -*-
import pytest

from health_check.backends.base import (
    BaseHealthCheckBackend, ServiceReturnedUnexpectedResult, ServiceUnavailable
)


class TestBaseHealthCheckBackend(object):
    def test_status(self):
        assert BaseHealthCheckBackend().status is None

    def test_error(self):
        with pytest.raises(Exception):
            BaseHealthCheckBackend().error(Exception, '.error() raises correctly', None)

    def test_unavailable(self):
        with pytest.raises(ServiceUnavailable):
            BaseHealthCheckBackend().unavailable('.unavailable() raises correctly')

    def test_unexpected(self):
        with pytest.raises(ServiceReturnedUnexpectedResult):
            BaseHealthCheckBackend().unexpected('.unexpected() raises correctly')
