import copy
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from health_check.plugins import plugin_dir


class MainView(TemplateView):
    template_name = 'health_check/index.html'

    @never_cache
    def get(self, request, *args, **kwargs):
        errors = []
        warnings = []

        plugins = sorted((
            plugin_class(**copy.deepcopy(options))
            for plugin_class, options in plugin_dir._registry
        ), key=lambda plugin: plugin.identifier())

        with ThreadPoolExecutor(max_workers=len(plugins) or 1) as executor:
            for plugin, error in zip(plugins, executor.map(self._run, plugins)):
                if plugin.critical:
                    errors.extend(error)
                else:
                    warnings.extend(error)

        status_code = 500 if errors else 200

        if 'application/json' in request.META.get('HTTP_ACCEPT', '') or \
           getattr(settings, 'HEALTHCHECK_JSON_RESPONSE_ONLY', False):
            return self.render_to_response_json(plugins, status_code)

        context = {'plugins': plugins, 'status_code': status_code}

        return self.render_to_response(context, status=status_code)

    def render_to_response_json(self, plugins, status_code):
        if getattr(settings, 'HEALTHCHECK_JSON_STATUS', False):
            return JsonResponse(
                {
                    str(p.identifier()): {
                        "status": str(p.pretty_status()),
                        "took": round(p.time_taken, 4)
                    } for p in plugins
                },
                status=status_code
            )
        else:
            return JsonResponse(
                {str(p.identifier()): str(p.pretty_status()) for p in plugins},
                status=status_code
            )

    def _run(self, plugin):
        plugin.run_check()
        try:
            return plugin.errors
        finally:
            from django.db import connection
            connection.close()
