import copy
import re
from concurrent.futures import ThreadPoolExecutor

from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from health_check.conf import HEALTH_CHECK
from health_check.exceptions import ServiceWarning
from health_check.plugins import plugin_dir


class MediaType:
    """
    Sortable object representing HTTP's accept header.

    .. seealso:: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept
    """

    pattern = re.compile(r'^(?P<mime_type>(\w+|\*)/([\w\d\-+.]+|\*))(; ?q=(?P<weight>[01](\.[\d3])?))?$')

    def __init__(self, mime_type, weight=1.0):
        self.mime_type = mime_type
        self.weight = float(weight)

    @classmethod
    def from_string(cls, value):
        """Return single instance parsed from given accept header string."""
        match = cls.pattern.search(value)
        if match is None:
            raise ValueError('"%s" is not a valid media type' % value)
        try:
            return cls(match.group('mime_type'), float(match.group('weight') or 1))
        except ValueError:
            return cls(value)

    @classmethod
    def parse_header(cls, value='*/*'):
        """Parse HTTP accept header and return instances sorted by weight."""
        yield from sorted((
            cls.from_string(token.strip())
            for token in value.split(',')
            if token.strip()
        ), reverse=True)

    def __str__(self):
        return "%s; q=%s" % (self.mime_type, self.weight)

    def __repr__(self):
        return "%s: %s" % (type(self).__name__, self.__str__())

    def __eq__(self, other):
        return self.weight == other.weight and self.mime_type == other.mime_type

    def __lt__(self, other):
        return self.weight.__lt__(other.weight)


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

        format_override = request.GET.get('format')

        if format_override == 'json':
            return self.render_to_response_json(plugins, status_code)

        accept_header = request.META.get('HTTP_ACCEPT', '*/*')
        context = {'plugins': plugins, 'status_code': status_code}
        for media in MediaType.parse_header(accept_header):
            if media.mime_type in ('text/html', 'application/xhtml+xml', 'text/*', '*/*'):
                return self.render_to_response(context, status=status_code)
            elif media.mime_type in ('application/json', 'application/*'):
                return self.render_to_response_json(plugins, status_code)
            else:
                return self.render_to_response(context, status=status_code)

    def render_to_response_json(self, plugins, status):
        return JsonResponse(
            {str(p.identifier()): str(p.pretty_status()) for p in plugins},
            status=status
        )
