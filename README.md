# django-health-check

[![version](https://img.shields.io/pypi/v/django-health-check.svg)](https://pypi.python.org/pypi/django-health-check/)
[![pyversion](https://img.shields.io/pypi/pyversions/django-health-check.svg)](https://pypi.python.org/pypi/django-health-check/)
[![djversion](https://img.shields.io/pypi/djversions/django-health-check.svg)](https://pypi.python.org/pypi/django-health-check/)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](https://pypi.python.org/pypi/django-health-check/)


This project checks for various conditions and provides reports when anomalous
behavior is detected.

The following health checks are bundled with this project:

- cache
- database
- storage
- disk and memory utilization (via `psutil`)
- AWS S3 storage
- Celery task queue
- Celery ping
- RabbitMQ
- Migrations
- Database Heartbeat (Lightweight version of `health_check.db`)

Writing your own custom health checks is also very quick and easy.

We also like contributions, so don't be afraid to make a pull request.

## Use Cases

The primary intended use case is to monitor conditions via HTTP(S), with
responses available in HTML and JSON formats. When you get back a response that
includes one or more problems, you can then decide the appropriate course of
action, which could include generating notifications and/or automating the
replacement of a failing node with a new one. If you are monitoring health in a
high-availability environment with a load balancer that returns responses from
multiple nodes, please note that certain checks (e.g., disk and memory usage)
will return responses specific to the node selected by the load balancer.

## Supported Versions

We officially only support the latest version of Python as well as the
latest version of Django and the latest Django LTS version.

## Installation

First, install the `django-health-check` package:

```shell
$ pip install django-health-check
```

Add the health checker to a URL you want to use:

```python
    urlpatterns = [
        # ...
        path(r'ht/', include('health_check.urls')),
    ]
```

Add the `health_check` applications to your `INSTALLED_APPS`:

```python
    INSTALLED_APPS = [
        # ...
        'health_check',                             # required
        'health_check.db',                          # stock Django health checkers
        'health_check.cache',
        'health_check.storage',
        'health_check.contrib.migrations',
        'health_check.contrib.celery',              # requires celery
        'health_check.contrib.celery_ping',         # requires celery
        'health_check.contrib.psutil',              # disk and memory utilization; requires psutil
        'health_check.contrib.s3boto3_storage',     # requires boto3 and S3BotoStorage backend
        'health_check.contrib.rabbitmq',            # requires RabbitMQ broker
        'health_check.contrib.redis',               # requires Redis broker
        'health_check.contrib.db_heartbeat',
    ]
```

**Note:** If using `boto 2.x.x` use `health_check.contrib.s3boto_storage`

(Optional) If using the `psutil` app, you can configure disk and memory
threshold settings; otherwise below defaults are assumed. If you want to disable
one of these checks, set its value to `None`.

```python
    HEALTH_CHECK = {
        'DISK_USAGE_MAX': 90,  # percent
        'MEMORY_MIN': 100,    # in MB
    }
```

To use Health Check Subsets, Specify a subset name and associate it with the relevant health check services to utilize Health Check Subsets. (New in version 3.18.0)
```python
    HEALTH_CHECK = {
        # .....
        "SUBSETS": {
            "startup-probe": ["MigrationsHealthCheck", "DatabaseBackend"],
            "liveness-probe": ["DatabaseBackend"],
            "<SUBSET_NAME>": ["<Health_Check_Service_Name>"]
        },
        # .....
    }
```

To only execute specific subset of health check
```shell
curl -X GET -H "Accept: application/json" http://www.example.com/ht/startup-probe/
```

If using the DB check, run migrations:

```shell
$ django-admin migrate
```

To use the RabbitMQ healthcheck, please make sure that there is a variable named
`BROKER_URL` on django.conf.settings with the required format to connect to your
rabbit server. For example:

```python
    BROKER_URL = "amqp://myuser:mypassword@localhost:5672/myvhost"
```

To use the Redis healthcheck, please make sure that there is a variable named ``REDIS_URL``
on django.conf.settings with the required format to connect to your redis server. For example:

```python
    REDIS_URL = "redis://localhost:6370"
```

The cache healthcheck tries to write and read a specific key within the cache backend.
It can be customized by setting `HEALTHCHECK_CACHE_KEY` to another value:

```python
    HEALTHCHECK_CACHE_KEY = "custom_healthcheck_key"
```

Additional connection options may be specified by defining a variable ``HEALTHCHECK_REDIS_URL_OPTIONS`` on the settings module.

## Setting up monitoring

You can use tools like Pingdom, StatusCake or other uptime robots to monitor service status.
The `/ht/` endpoint will respond with an HTTP 200 if all checks passed
and with an HTTP 500 if any of the tests failed.
Getting machine-readable JSON reports

If you want machine-readable status reports you can request the `/ht/`
endpoint with the `Accept` HTTP header set to `application/json`
or pass `format=json` as a query parameter.

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
        name = 'my_app'

        def ready(self):
            from .backends import MyHealthCheckBackend
            plugin_dir.register(MyHealthCheckBackend)
```

Make sure the application you write the checker into is registered in your
`INSTALLED_APPS`.

## Customizing output

You can customize HTML or JSON rendering by inheriting from `MainView` in
`health_check.views` and customizing the `template_name`, `get`, `render_to_response`
and `render_to_response_json` properties:

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

    # urls.py
    import views

    urlpatterns = [
        # ...
        path(r'ht/', views.HealthCheckCustomView.as_view(), name='health_check_custom'),
    ]
```

## Django command

You can run the Django command `health_check` to perform your health checks via the command line,
or periodically with a cron, as follow:

```shell
    django-admin health_check
```

This should yield the following output:

```
    DatabaseHealthCheck      ... working
    CustomHealthCheck        ... unavailable: Something went wrong!
```

Similar to the http version, a critical error will cause the command to quit with the exit code `1`.


## Other resources

- [django-watchman](https://github.com/mwarkentin/django-watchman) is a package that does some of the same things in a slightly different way.
