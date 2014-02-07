
import json

from django.http import HttpResponse, HttpResponseServerError
from django.template import loader
from health_check.utils import get_plugins


def home(request):
    plugins, working = get_plugins()

    if working:
        return HttpResponse(loader.render_to_string("health_check/dashboard.html", {'plugins': plugins}))
    else:
        return HttpResponseServerError(loader.render_to_string("health_check/dashboard.html", {'plugins': plugins}))

def jsonhealthcheck(request):
    plugins, working = get_plugins()

    health_check_status = {}
    for plugin in plugins:
            health_check_status[str(plugin.identifier())] = str(plugin.pretty_status())

    health_check_json = json.dumps(health_check_status)
    return HttpResponse(health_check_json, mimetype='application/json')