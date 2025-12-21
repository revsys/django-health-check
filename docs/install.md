# Installation

Add the `django-health-check` package to your project:

```shell
uv add django-health-check
# or
pip install django-health-check
```

Add the health checker to a URL you want to use:

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    # ...
    path("ht/", include("health_check.urls")),
]
```

Add the `health_check` applications to your `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "health_check",  # required
    "health_check.db",  # stock Django health checkers
    "health_check.cache",
    "health_check.storage",
    "health_check.contrib.migrations",
    "health_check.contrib.celery",  # requires celery
    "health_check.contrib.celery_ping",  # requires celery
    "health_check.contrib.psutil",  # disk and memory utilization; requires psutil
    "health_check.contrib.s3boto3_storage",  # requires boto3 and S3BotoStorage backend
    "health_check.contrib.rabbitmq",  # requires RabbitMQ broker
    "health_check.contrib.redis",  # requires Redis broker
]
```

(Optional) If using the `psutil` app, you can configure disk and memory
threshold settings; otherwise below defaults are assumed. If you want to
disable one of these checks, set its value to `None`.

```python
# settings.py
HEALTH_CHECK = {
    "DISK_USAGE_MAX": 90,  # percent
    "MEMORY_MIN": 100,  # in MB
}
```

If using the DB check, run migrations:

```shell
django-admin migrate
```

To use the RabbitMQ healthcheck, please make sure that there is a
variable named `BROKER_URL` on django.conf.settings with the required
format to connect to your rabbit server. For example:

```python
# settings.py
BROKER_URL = "amqp://myuser:mypassword@localhost:5672/myvhost"
```

To use the Redis healthcheck, please make sure that there is a variable
named `REDIS_URL` on django.conf.settings with the required format to
connect to your redis server. For example:

```python
# settings.py
REDIS_URL = "redis://localhost:6370"
```

The cache healthcheck tries to write and read a specific key within the
cache backend. It can be customized by setting `HEALTHCHECK_CACHE_KEY`
to another value:

```python
# settings.py
HEALTHCHECK_CACHE_KEY = "custom_healthcheck_key"
```
