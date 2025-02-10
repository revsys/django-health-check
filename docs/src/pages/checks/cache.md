---
title: Cache Health Check
pageTitle: django-health-check cache check
description: Verify that the Django application's caching system is operating seamlessly and efficiently
---

Caching is storing the outcome of a time-consuming calculation to avoid recomputing in the future.

The `health_check.cache` verifies that the Django application
caching mechanism is functioning as intended.


## Settings

The settings that need to be correct are the standard Django `CACHES`
settings in your `settings.py`.  
To ensure that you have configured Caching properly go through this 
[documentation](https://docs.djangoproject.com/en/4.2/topics/cache/)

## What does it check?

This check does the following:

- Reads the cache backend's configuration
- Writes to the cache backend
- Reads from the cache backend
- Checks for timeouts
- Deletes the test data from the cache backend
- Returns status 

This ensures your app's cache backend is functioning correctly and is always available. It not only prevents [data inconsistencies](https://www.alachisoft.com/blogs/cache-database-data-inconsistency-pitfall-and-solutions/#:~:text=Data%20inconsistency%20issues%20occur%20when,the%20cache%20is%20not%20synchronized) and [race conditions](https://www.techtarget.com/searchstorage/definition/race-condition) but also helps identify and troubleshoot cache-related problems.

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

3.Add the `health_check.cache` applications to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'health_check',                             
    'health_check.cache',
]
```
4.The cache healthcheck tries to write and read a specific key within the cache backend. 
It can be customized by setting `HEALTHCHECK_CACHE_KEY` in the `settings.py` file to another value:

```python
HEALTHCHECK_CACHE_KEY = "custom_health_check_key"
```

5.Run the health check
```shell
python manage.py health_check

```