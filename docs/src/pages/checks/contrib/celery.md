---
title: Celery Health Check
pageTitle: django-health-check celery check
description: Verify the Celery tasks are executed successfully.
---

The `health_check.contrib.celery` verifies that the Celery tasks
 can be executed successfully within a specified timeout period

Ensure that you have celery installed and configured in your application.

Information about how to properly configure celery with django
is [here](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html)


## Settings

The settings that need to be correct are  `HEALTHCHECK_CELERY_RESULT_TIMEOUT`
and `HEALTHCHECK_CELERY_QUEUE_TIMEOUT` in your `settings.py`.  

## What does it check?

This check does the following:

- Checks celery worker status 
- Checks that the celery workers can execute tasks
- Results are returned within specified time limits

Celery health checks helps you catch potential issues early, ensures proper configuration, 
and provides insights into the real-time status of your Celery workers.


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

3.Add the `health_check.contrib.celery` applications to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'health_check',                             
    'health_check.contrib.celery',
]

# Set the timeout for waiting for Celery task results (in seconds)
HEALTHCHECK_CELERY_RESULT_TIMEOUT = 3  # this is the default time, Adjust the value as needed

# Set the timeout for the expiration of the Celery task in the queue (in seconds)
HEALTHCHECK_CELERY_QUEUE_TIMEOUT = 3 #this is the default time, Adjust the value as needed

#..... other celery settings.....

```
4.Run the health check
```shell
python manage.py health_check

```