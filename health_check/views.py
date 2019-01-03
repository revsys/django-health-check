import copy

from abc import ABC, abstractmethod

from concurrent.futures import ThreadPoolExecutor

from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from health_check.conf import HEALTH_CHECK
from health_check.exceptions import ServiceWarning
from health_check.plugins import plugin_dir


class Status(object):
    def __init__(self, plugins, status_code):
        self.plugins = plugins
        self.status_code = status_code

    def get_context(self):
        return {'plugins': self.plugins, 'status_code': self.status_code}


class AbstractMainView(ABC, TemplateView):
    @staticmethod
    def _get_status():
        errors = []

        plugins = sorted((
            plugin_class(**copy.deepcopy(options))
            for plugin_class, options in plugin_dir._registry
        ), key=lambda plugin: plugin.identifier())

        def _run(plugin):
            plugin.run_check()
            try:
                return plugin
            finally:
                from django.db import connection
                connection.close()

        with ThreadPoolExecutor(max_workers=len(plugins) or 1) as executor:
            for plugin in executor.map(_run, plugins):
                if plugin.critical_service:
                    if not HEALTH_CHECK['WARNINGS_AS_ERRORS']:
                        errors.extend(
                            e for e in plugin.errors
                            if not isinstance(e, ServiceWarning)
                        )
                    else:
                        errors.extend(plugin.errors)

        status_code = 500 if errors else 200

        return Status(plugins, status_code)

    template_name = 'health_check/index.html'

    def get_html_response(self):
        status = self._get_status()
        return self.render_to_response(status.get_context(), status=status.status_code)

    def get_json_response(self):
        status = self._get_status()
        return JsonResponse(
            {str(p.identifier()): str(p.pretty_status()) for p in status.plugins},
            status=status.status_code
        )

    @abstractmethod
    def get(self, request, *args, **kwargs):
        pass


class HtmlFirstView(AbstractMainView):
    @never_cache
    def get(self, request, *args, **kwargs):
        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            return self.get_json_response()
        return self.get_html_response()


class JsonFirstView(AbstractMainView):
    @never_cache
    def get(self, request, *args, **kwargs):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return self.get_html_response()
        return self.get_json_response()


class MainView(HtmlFirstView):
    pass
