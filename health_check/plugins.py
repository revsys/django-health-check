# -*- coding: utf-8 -*-


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class HealthCheckPluginDirectory(object):
    """Django health check registry."""

    def __init__(self):
        self._registry = {}  # plugin_class class -> plugin options

    def reset(self):
        """Reset registry state, e.g. for testing purposes."""
        self._registry = {}

    def register(self, plugin, **options):
        """Add the given plugin from the registry."""
        if plugin in self._registry:
            raise AlreadyRegistered('The plugin %s is already registered' % plugin.__name__)
        # Instantiate the admin class to save in the registry
        self._registry[plugin] = options

    def unregister(self, plugin):
        """Remove the given plugin from the registry."""
        if plugin not in self._registry:
            raise NotRegistered('The plugin %s is not registered' % plugin.__name__)
        del self._registry[plugin]


plugin_dir = HealthCheckPluginDirectory()
