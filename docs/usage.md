# Usage

## Setting up monitoring

You can use tools like Pingdom, StatusCake or other uptime robots to
monitor service status. The `/ht/` endpoint will respond with an HTTP
200 if all checks passed and with an HTTP 500 if any of the tests
failed. Getting machine-readable JSON reports

If you want machine-readable status reports you can request the `/ht/`
endpoint with the `Accept` HTTP header set to `application/json` or pass
`format=json` as a query parameter.

The backend will return a JSON response:

```shell
$ curl -v -X GET -H "Accept: application/json" http://www.example.com/ht/

> GET /ht/ HTTP/1.1
> Host: www.example.com
> Accept: application/json
>
< HTTP/1.1 200 OK
< Content-Type: application/json

{
    "CacheBackend": "working",
    "DatabaseBackend": "working",
    "S3BotoStorageHealthCheck": "working"
}

$ curl -v -X GET http://www.example.com/ht/?format=json

> GET /ht/?format=json HTTP/1.1
> Host: www.example.com
>
< HTTP/1.1 200 OK
< Content-Type: application/json

{
    "CacheBackend": "working",
    "DatabaseBackend": "working",
    "S3BotoStorageHealthCheck": "working"
}
```

## Writing a custom health check

Writing a health check is quick and easy:

```python
from health_check.backends import BaseHealthCheckBackend


class MyHealthCheckBackend(BaseHealthCheckBackend):
    #: The status endpoints will respond with a 200 status code
    #: even if the check errors.
    critical_service = False

    def check_status(self):
        # The test code goes here.
        # You can use `self.add_error` or
        # raise a `HealthCheckException`,
        # similar to Django's form validation.
        pass

    def identifier(self):
        return self.__class__.__name__  # Display name on the endpoint.
```

After writing a custom checker, register it in your app configuration:

```python
from django.apps import AppConfig

from health_check.plugins import plugin_dir


class MyAppConfig(AppConfig):
    name = "my_app"

    def ready(self):
        from .backends import MyHealthCheckBackend

        plugin_dir.register(MyHealthCheckBackend)
```

Make sure the application you write the checker into is registered in
your `INSTALLED_APPS`.

## Customizing output

You can customize HTML or JSON rendering by inheriting from `MainView`
in `health_check.views` and customizing the `template_name`, `get`,
`render_to_response` and `render_to_response_json` properties:

```python
# views.py
from django.http import HttpResponse, JsonResponse

from health_check.views import MainView


class HealthCheckCustomView(MainView):
    template_name = "myapp/health_check_dashboard.html"  # customize the used templates

    def get(self, request, *args, **kwargs):
        plugins = []
        status = 200  # needs to be filled status you need
        # ...
        if "application/json" in request.META.get("HTTP_ACCEPT", ""):
            return self.render_to_response_json(plugins, status)
        return self.render_to_response(plugins, status)

    def render_to_response(self, plugins, status):  # customize HTML output
        return HttpResponse("COOL" if status == 200 else "SWEATY", status=status)

    def render_to_response_json(self, plugins, status):  # customize JSON output
        return JsonResponse(
            {str(p.identifier()): "COOL" if status == 200 else "SWEATY" for p in plugins}, status=status
        )


# urls.py
from django.urls import path

from . import views

urlpatterns = [
    # ...
    path(r"^ht/$", views.HealthCheckCustomView.as_view(), name="health_check_custom"),
]
```

## Django command

You can run the Django command `health_check` to perform your health
checks via the command line, or periodically with a cron, as follows:

```shell
django-admin health_check
```

This should yield the following output:

```
DatabaseHealthCheck      ... working
CustomHealthCheck        ... unavailable: Something went wrong!
```

Similar to the http version, a critical error will cause the command to
quit with the exit code `1`.
