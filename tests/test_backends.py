import logging
from io import StringIO

import pytest

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException


class TestBaseHealthCheckBackend:

    def test_run_check(self):
        with pytest.raises(NotImplementedError):
            BaseHealthCheckBackend().run_check()

    def test_identifier(self):
        assert BaseHealthCheckBackend().identifier() == 'BaseHealthCheckBackend'

        class MyHeathCheck(BaseHealthCheckBackend):
            pass

        assert MyHeathCheck().identifier() == 'MyHeathCheck'

        class MyHeathCheck(BaseHealthCheckBackend):
            foo = 'bar'

            def identifier(self):
                return self.foo

        assert MyHeathCheck().identifier() == 'bar'

    def test_status(self):
        ht = BaseHealthCheckBackend()
        assert ht.status == 1
        ht.errors = [1]
        assert ht.status == 0

    def test_pretty_status(self):
        ht = BaseHealthCheckBackend()
        assert ht.pretty_status() == 'working'
        ht.errors = ['foo']
        assert ht.pretty_status() == 'foo'
        ht.errors.append('bar')
        assert ht.pretty_status() == 'foo\nbar'
        ht.errors.append(123)
        assert ht.pretty_status() == 'foo\nbar\n123'

    def test_add_error(self):
        ht = BaseHealthCheckBackend()
        e = HealthCheckException('foo')
        ht.add_error(e)
        assert ht.errors[0] is e

        ht = BaseHealthCheckBackend()
        ht.add_error('bar')
        assert isinstance(ht.errors[0], HealthCheckException)
        assert str(ht.errors[0]) == 'unknown error: bar'

        ht = BaseHealthCheckBackend()
        ht.add_error(type)
        assert isinstance(ht.errors[0], HealthCheckException)
        assert str(ht.errors[0]) == 'unknown error: unknown error'

    def test_add_error_cause(self):
        ht = BaseHealthCheckBackend()
        logger = logging.getLogger('health-check')
        with StringIO() as stream:
            stream_handler = logging.StreamHandler(stream)
            logger.addHandler(stream_handler)
            try:
                raise Exception('bar')
            except Exception as e:
                ht.add_error('foo', e)

            stream.seek(0)
            log = stream.read()
            assert 'foo' in log
            assert 'bar' in log
            assert 'Traceback' in log
            assert 'Exception: bar' in log
            logger.removeHandler(stream_handler)

        with StringIO() as stream:
            stream_handler = logging.StreamHandler(stream)
            logger.addHandler(stream_handler)
            try:
                raise Exception('bar')
            except Exception:
                ht.add_error('foo')

            stream.seek(0)
            log = stream.read()
            assert 'foo' in log
            assert 'bar' not in log
            assert 'Traceback' not in log
            assert 'Exception: bar' not in log
            logger.removeHandler(stream_handler)
