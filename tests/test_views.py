import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from health_check.plugins import plugin_dir
from health_check_cache.plugin_health_check import CacheBackend


class HealthCheckViewsTest(TestCase):
    """
    Test that basic views return correct looking data.
    Add plugins you wish to use in this test to the ``plugins`` tuple.
    This way we avoid setting up a Django project just for testing.
    """

    plugins = (
        CacheBackend,
    )

    def setUp(self):
        for plugin in self.plugins:
            plugin_dir.register(plugin)

    def tearDown(self):
        plugin_dir.unregister(self.plugins)

    def check_health_check_response(self, response):
        self.assertEqual(response.status_code, 200)
        for plugin in self.plugins:
            self.assertContains(response, plugin.__name__)

    def test_home(self):
        response = self.client.get(reverse('health_check_home'))
        self.check_health_check_response(response)

    def test_home_json(self):
        response = self.client.get(reverse('health_check_home'), HTTP_ACCEPT='application/json')
        self.check_health_check_response(response)
        self.assertEqual(json.loads(response.content.decode('utf-8'))['CacheBackend'], 'OK')
