---
title: Storage Health Check
pageTitle: django-health-check storage check
description: Verify the health of your django application's storage
---

The `health_check.storage` verifies that the Django application's storage backend is working
as should.

## Settings

The settings that need to be correct are the standard Django `STORAGES`
settings in your `settings.py`.  
The default storage settings can be found
[here](https://docs.djangoproject.com/en/4.2/ref/settings/#storages)

## What does it check?

This check does the following:

- Reads the storage backend's configuration
- Writes to the storage backend
- Reads from the storage backend
- Checks for timeouts
- Deletes the test file from the storage backend
- Return status 

This ensures your app's storage backend is functioning correctly and detects any storage issues that may affect performance.

### Steps
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

3.Add the `health_check.storage` applications to your `INSTALLED_APPS`:

``` python
INSTALLED_APPS = [
    # ...
    'health_check',                             
    'health_check.storage',
]
```
4.Run the health check
```shell
python manage.py health_check

```