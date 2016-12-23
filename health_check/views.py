# -*- coding: utf-8 -*-
import json
from django.http import HttpResponse, HttpResponseServerError
from django.template import loader

from health_check.plugins import plugin_dir

RESPONSE_METHOD = (HttpResponseServerError, HttpResponse)


def _base():
    plugins = []
    working = True
    for plugin_class, plugin in plugin_dir._registry.items():
        plugin = plugin_class()
        if not plugin.status:  # Will return True or None
            working = False
        plugins.append(plugin)
    plugins.sort(key=lambda x: x.identifier())
    return working, plugins


def home(request):
    working, plugins = _base()
    method = RESPONSE_METHOD[1 if working else 0]
    return method(loader.render_to_string(
        "health_check/dashboard.html", {'plugins': plugins}))


def json_view(request):
    working, plugins = _base()
    data = {p.identifier(): p.json_status() for p in plugins}
    method = RESPONSE_METHOD[1 if working else 0]
    return method(json.dumps(data, indent=2), content_type="application/json")
