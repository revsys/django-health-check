---
title: Migrations Health Check
pageTitle: django-health-check migrations check
description: Verify the status of your application's migrations 
---

The `health_check.contrib.migrations` verifies that the Django application's migrations are
 up-to-date and applied to the database

## What does it check?

This check does the following:

- Checks for applied migrations
- Checks for pending migrations 
- Checks for migration version mismatch
- Checks for Stale Content Types

This prevents data corruption by ensuring that the schema is up to date and maintains
data integrity ensuring that it is consistent with the code. 


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

3.Add the `health_check.contrib.migrations` applications to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'health_check',                             
    'health_check.contrib.migrations',
]
```
4.Run the health check
```shell
python manage.py health_check

```