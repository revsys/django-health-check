import logging
import pprint
import re

from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response

from health_check.health_serializer import HealthSerializer
from health_check.mixins import CheckMixin


class MediaType:
    """
    Sortable object representing HTTP's accept header.

    .. seealso:: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept
    """

    pattern = re.compile(
        r"""
          ^
          (?P<mime_type>
            (\w+|\*)                      # Media type, or wildcard
            /
            ([\w\d\-+.]+|\*)              # subtype, or wildcard
          )
          (
            \s*;\s*                       # parameter separator with optional whitespace
            q=                            # q is expected to be the first parameter, by RFC2616
            (?P<weight>
              1([.]0{1,3})?               # 1 with up to three digits of precision
              |
              0([.]\d{1,3})?              # 0.000 to 0.999 with optional precision
            )
          )?
          (
            \s*;\s*                       # parameter separator with optional whitespace
            [-!#$%&'*+.^_`|~0-9a-zA-Z]+   # any token from legal characters
            =
            [-!#$%&'*+.^_`|~0-9a-zA-Z]+   # any value from legal characters
          )*
          $
        """, re.VERBOSE)

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


class MainView(CheckMixin, generics.RetrieveAPIView):
    template_name = 'health_check/index.html'
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    serializer_class = HealthSerializer

    def get(self, request, *args, **kwargs):
        status_code = 500 if self.errors else 200
        serializer = self.get_serializer(self.plugins)
        return Response(serializer.data, template_name=self.template_name, status=status_code)
