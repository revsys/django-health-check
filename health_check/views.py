from django.http import HttpResponse, HttpResponseServerError
from django.template import loader
from health_check.plugins import plugin_dir
from health_check.backends.base import HealthCheckStatusType
def home(request):
    plugins = []
    working = True
    
    for plugin_class, plugin in plugin_dir._registry.items():
        plugin = plugin_class()
        if plugin.status != HealthCheckStatusType.working:
            working = False
        plugins.append(plugin)
    plugins.sort(key=lambda x: x.identifier)

    if working:
        return HttpResponse(loader.render_to_string("health_check/dashboard.html", {'plugins': plugins}))
    else:
        return HttpResponseServerError(loader.render_to_string("health_check/dashboard.html", {'plugins': plugins}))