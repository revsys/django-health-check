import copy
from concurrent.futures import ThreadPoolExecutor

from health_check.backends import CommonHealth
from health_check.conf import HEALTH_CHECK
from health_check.exceptions import ServiceWarning
from health_check.plugins import plugin_dir


class CheckMixin:
    _errors = None
    _plugins = None
    _common_health = None

    @property
    def errors(self):
        if not self._errors:
            self._errors = self.run_check()
        return self._errors

    @property
    def plugins(self):
        if not self._plugins:
            self._plugins = sorted((
                plugin_class(**copy.deepcopy(options))
                for plugin_class, options in plugin_dir._registry
            ), key=lambda plugin: plugin.identifier())
        return self._plugins

    @property
    def common_health(self):
        if not self._common_health:
            self._common_health = CommonHealth()
            self._plugins.append(self._common_health)
        return self._common_health

    def run_check(self):
        errors = []

        def _run(plugin):
            plugin.run_check()
            try:
                return plugin
            finally:
                from django.db import connections
                connections.close_all()

        error_plugins = []
        with ThreadPoolExecutor(max_workers=len(self.plugins) or 1) as executor:
            for plugin in executor.map(_run, self.plugins):
                if plugin.errors:
                    error_plugins.append(plugin.identifier())

                if plugin.critical_service:
                    if not HEALTH_CHECK['WARNINGS_AS_ERRORS']:
                        errors.extend(
                            e for e in plugin.errors
                            if not isinstance(e, ServiceWarning)
                        )
                    else:
                        errors.extend(plugin.errors)

        self.common_health.run_check(external_errors=error_plugins)

        return errors
