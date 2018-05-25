import copy
from concurrent.futures import ThreadPoolExecutor

from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from health_check.conf import HEALTH_CHECK
from health_check.exceptions import ServiceWarning
from health_check.plugins import plugin_dir


class MainView(TemplateView):
    template_name = 'health_check/index.html'

    @never_cache
    def get(self, request, *args, **kwargs):
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

        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            return self.render_to_response_json(plugins, status_code)

        context = {'plugins': plugins, 'status_code': status_code}

        return self.render_to_response(context, status=status_code)

    def render_to_response_json(self, plugins, status):
        return JsonResponse(
            {str(p.identifier()): str(p.pretty_status()) for p in plugins},
            status=status
        )
