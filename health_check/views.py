
import json

from django.http import HttpResponse, HttpResponseServerError
from django.template import loader
from health_check.plugins import plugin_dir


def home(request):
    plugins = []
    working = True
    for plugin_class, plugin in plugin_dir._registry.items():
        plugin = plugin_class()
        if not plugin.status:  # Will return True or None
            working = False
        plugins.append(plugin)
    plugins.sort(key=lambda x: x.identifier())

    if working:
        return HttpResponse(loader.render_to_string("health_check/dashboard.html", {'plugins': plugins}))
    else:
        return HttpResponseServerError(loader.render_to_string("health_check/dashboard.html", {'plugins': plugins}))

def jsonhealthcheck(request):
    plugins = []
    working = True
    for plugin_class, plugin in plugin_dir._registry.items():
        plugin = plugin_class()
        if not plugin.status:  # Will return True or None
            working = False
        plugins.append(plugin)
    plugins.sort(key=lambda x: x.identifier())

    health_check_status = {}
    for plugin in plugins:
            health_check_status[str(plugin.identifier())] = str(plugin.pretty_status())

    health_check_json = json.dumps(health_check_status)
    return HttpResponse(health_check_json, mimetype='application/json')