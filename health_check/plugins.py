# This is heavily inspired by the django admin sites.py

from health_check.backends.base import BaseHealthCheckBackend

class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class HealthCheckPluginDirectory(object):

    def __init__(self):
        self._registry = {} # model_class class -> admin_class instance

    def register(self, plugin, admin_class=None, **options):
        if plugin in self._registry:
            raise AlreadyRegistered('The model %s is already registered' % plugin.__name__)
        # Instantiate the admin class to save in the registry
        self._registry[plugin] = plugin()

    def unregister(self, model_or_iterable):
        if isinstance(model_or_iterable, BaseHealthCheckBackend):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model not in self._registry:
                raise NotRegistered('The model %s is not registered' % model.__name__)
            del self._registry[model]


plugin_dir = HealthCheckPluginDirectory()