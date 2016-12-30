# -*- coding: utf-8 -*-
import copy

from django.http import HttpResponse, HttpResponseServerError
from django.template import loader

from health_check.plugins import plugin_dir


def home(request):
    plugins = []
    errors = []
    for plugin_class, options in plugin_dir._registry.items():
        plugin = plugin_class(**copy.deepcopy(options))
        plugin.run_check()
        plugins.append(plugin)
        errors += plugin.errors
    plugins.sort(key=lambda x: x.identifier())
    if errors:
        return HttpResponseServerError(loader.render_to_string("health_check/dashboard.html", {'plugins': plugins}))
    else:
        return HttpResponse(loader.render_to_string("health_check/dashboard.html", {'plugins': plugins}))
