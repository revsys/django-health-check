---
title: Custom django-health-check output
pageTitle: Writing custom django-health-check output
description: How to write your own health checks output.
---
Customizing your output comes in handy when you need to match the needs your 
application or integrate with specific frontend tools and monitoring tools

You can customize your output (HTML or JSON) rendering by inheriting from MainView in 
`health_check.views` and customize the `template_name`,` get`, `render_to_response `and
 `render_to_response_json` properties:

```python
# views.py
from health_check.views import MainView

class HealthCheckCustomView(MainView):
    template_name = 'myapp/health_check_dashboard.html'  # customize the used templates

    def get(self, request, *args, **kwargs):
        plugins = []
        status = 200 # needs to be filled status you need
        # ...
        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            return self.render_to_response_json(plugins, status)
        return self.render_to_response(plugins, status)

    def render_to_response(self, plugins, status):       # customize HTML output
        return HttpResponse('COOL' if status == 200 else 'SWEATY', status=status)

    def render_to_response_json(self, plugins, status):  # customize JSON output
        return JsonResponse(
            {str(p.identifier()): 'COOL' if status == 200 else 'SWEATY' for p in plugins},
            status=status
        )
```

```python
# urls.py
import views

urlpatterns = [
    # ...
    url(r'^ht/$', views.HealthCheckCustomView.as_view(), name='health_check_custom'),
]
```
