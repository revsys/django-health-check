---
title: Redis Health Check
pageTitle: django-health-check redis check
description: Verifies that the Redis service is healthy and responsive
---

The `health_check.contrib.redis` verifies that the Redis service is healthy and responsive.

Ensure that you have [Redis](https://pypi.org/project/redis/) installed.

## Settings

The setting that needs to be correct is `REDIS_URL` in your `settings.py` to connect to your Redis server.  

```python 
REDIS_URL = "redis://localhost:6370"
```

## What does it check?

This check does the following:

- Retrieves Redis URL from the settings 
- Connects to the Redis instance
- Pings the Redis instance

Through performing this checks, potential issues with Redis are identified and corrective action taken to
maintain health and stability of the application.


## Steps
1.Installation
 ```shell
#requirements.txt
django-health-check == x.x.x
```

2.Configure your health check URL endpoint:

```python
urlpatterns = [
    # ... your existing URLs here ...
    url(r'^health/', include('health_check.urls')),
]
```

3.Add the `health_check.contrib.redis` applications to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'health_check',                             
    'health_check.contrib.redis',
]

REDIS_URL = "redis://localhost:6370"

```

4.Run the health check
```shell
python manage.py health_check

```