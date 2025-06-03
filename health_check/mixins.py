import copy
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

from django.http import Http404

from health_check.conf import HEALTH_CHECK
from health_check.exceptions import ServiceWarning
from health_check.plugins import plugin_dir


class CheckMixin:
    _errors = None
    _plugins = None

    @property
    def errors(self):
        if not self._errors:
            self._errors = self.run_check()
        return self._errors

    def check(self, subset=None):
        return self.run_check(subset=subset)

    @property
    def plugins(self):
        if not plugin_dir._registry:
            return OrderedDict({})

        if not self._plugins:
            registering_plugins = (
                plugin_class(**copy.deepcopy(options)) for plugin_class, options in plugin_dir._registry
            )
            registering_plugins = sorted(registering_plugins, key=lambda plugin: plugin.identifier())
            self._plugins = OrderedDict({plugin.identifier(): plugin for plugin in registering_plugins})
        return self._plugins

    def filter_plugins(self, subset=None):
        if subset is None:
            return self.plugins

        health_check_subsets = HEALTH_CHECK["SUBSETS"]
        if subset not in health_check_subsets or not self.plugins:
            raise Http404(f"Subset: '{subset}' does not exist.")

        selected_subset = set(health_check_subsets[subset])
        return {
            plugin_identifier: v
            for plugin_identifier, v in self.plugins.items()
            if plugin_identifier in selected_subset
        }

    def run_check(self, subset=None):
        errors = []

        def _run(plugin):
            plugin.run_check()
            try:
                return plugin
            finally:
                from django.db import connections

                connections.close_all()

        def _collect_errors(plugin):
            if plugin.critical_service:
                if not HEALTH_CHECK["WARNINGS_AS_ERRORS"]:
                    errors.extend(e for e in plugin.errors if not isinstance(e, ServiceWarning))
                else:
                    errors.extend(plugin.errors)

        plugins = self.filter_plugins(subset=subset)
        plugin_instances = plugins.values()

        if HEALTH_CHECK["DISABLE_THREADING"]:
            for plugin in plugin_instances:
                _run(plugin)
                _collect_errors(plugin)
        else:
            with ThreadPoolExecutor(max_workers=len(plugin_instances) or 1) as executor:
                for plugin in executor.map(_run, plugin_instances):
                    _collect_errors(plugin)
        return errors
