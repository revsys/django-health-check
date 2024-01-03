---
title: Celery Ping Health Check
pageTitle: django-health-check celery ping check
description: Verify that Celery pings  Celery workers and checks the responses. 
---

The `health_check.contrib.celery_ping` verifies that the celery 
task queues have active workers.

Ensure that you have celery installed and configured in your application.

Information about how to properly configure celery with django
is [here](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html)


## Settings

The setting that needs to be correct is the `HEALTHCHECK_CELERY_PING_TIMEOUT` in your `settings.py`.  

## What does it check?
This check does the following:

- Pings celery workers and checks their responses
- Verify availability of the celery workers
- Check if celery task queues have active workers

Celery ping health checks helps you to diagnose and address problems 
with Celery worker availability and correctness.


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
 
3.Add the `health_check.contrib.celery_ping` applications 
to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'health_check',                             
    'health_check.contrib.celery_ping',
]

# Set the timeout for waiting for Celery ping result (in seconds)
HEALTHCHECK_CELERY_PING_TIMEOUT = 1  # this is the default time, Adjust the value as needed


#..... other celery settings.....

```
4.Run the health check
```shell
python manage.py health_check

```

**Note:** 
The major difference between `health_check.contrib.celery_ping` and `health_check.contrib.celery`
is that the `health_check.contrib.celery_ping`  checks for worker responsiveness and readiness while  
`health_check.contrib.celery`checks on task execution health
