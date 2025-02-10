---
title: Database Health Check
pageTitle: django-health-check database check
description: Verify your Django application is able to communicate with the database server
---

The `health_check.db` health check verifies that both Django and your database
server are both configured and functioning properly.

## Settings

The only settings that need to be correct are the standard Django `DATABASES`
settings in your `settings.py`.

## What does it check?

This check does the following:

- Creates a new row in a Django ORM model for this app
- Updates that row with a new value
- Deletes the row

This ensures your app can communicate with the database and that it's able to
write new rows.

The idea is if you can write and update a row in a specific Django model
your app can most likely read and write rows to any of it's models without an
issue.

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

3.Add the `health_check.db` applications to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'health_check',                             
    'health_check.db',
]
```

4.Run migrations
```shell
 python manage.py migrate
```

5.Run the health check
```shell
python manage.py health_check

```