from django.core.cache.backends.base import BaseCache, CacheKeyWarning
from django.test import TestCase
from mock import patch

from health_check.cache.backends import CacheBackend


# A Mock version of the cache to use for testing
class MockCache(BaseCache):
    """
    A Mock Cache used for testing.
    set_works - set to False to make the mocked set method fail, but not raise
    set_raises - The Exception to be raised when set() is called, if any
    """
    key = None
    value = None
    set_works = None
    set_raises = None

    def __init__(self, set_works=True, set_raises=None):
        super(MockCache, self).__init__(params={})
        self.set_works = set_works
        self.set_raises = set_raises

    def set(self, key, value, *args, **kwargs):
        if self.set_raises is not None:
            raise self.set_raises
        elif self.set_works:
            self.key = key
            self.value = value
        else:
            self.key = key
            self.value = None

    def get(self, key, *args, **kwargs):
        if key == self.key:
            return self.value
        else:
            return None


class HealthCheckCacheTests(TestCase):
    """
    Tests health check behavior with a mocked cache backend.
    Ensures check_status returns/raises the expected result when the cache works, fails, or raises exceptions.
    """

    @patch("health_check.cache.backends.cache", MockCache())
    def test_check_status_working(self):
        cache_backend = CacheBackend()
        cache_backend.run_check()
        self.assertFalse(cache_backend.errors)

    # check_status should raise ServiceUnavailable when values at cache key do not match
    @patch("health_check.cache.backends.cache", MockCache(set_works=False))
    def test_set_fails(self):
        cache_backend = CacheBackend()
        cache_backend.run_check()
        self.assertTrue(cache_backend.errors)
        self.assertIn('unavailable: Cache key does not match', cache_backend.pretty_status())

    # check_status should catch generic exceptions raised by set and convert to ServiceUnavailable
    @patch("health_check.cache.backends.cache", MockCache(set_raises=Exception))
    def test_set_raises_generic(self):
        cache_backend = CacheBackend()
        with self.assertRaises(Exception):
            cache_backend.run_check()

    # check_status should catch CacheKeyWarning and convert to ServiceReturnedUnexpectedResult
    @patch("health_check.cache.backends.cache", MockCache(set_raises=CacheKeyWarning))
    def test_set_raises_cache_key_warning(self):
        cache_backend = CacheBackend()
        cache_backend.check_status()
        cache_backend.run_check()
        self.assertIn('unexpected result: Cache key warning', cache_backend.pretty_status())
