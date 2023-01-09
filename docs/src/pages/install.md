---
title: Installing django-health-check
pageTitle: django-health-check - Installation
description: How to install and set up django-health-check
---

Installing and setting up django-health-check is relatively straight forward.

First, you will need to install the library from PyPI:

```shell
pip install django-health-check
```

Since you are someone who takes their Django application's health seriously,
you will want to pin the version of this library in your requirements.txt to
avoid a newer version of the library accidentally breaking things when it is
released.

## Setup the URLs

After it is installed you need to configure your health check URL endpoint:

```python
urlpatterns = [
    # ... your existing URLs here ...
    url(r'^health/', include('health_check.urls')),
]
```

Keep in mind, you don't have to call your endpoint `/health/` you could use
`/ht/`, `/_checks/` or any name you like.

## Configuring checks in Django Settings

The way you enable individual health checks is by including them in your
project's `INSTALLED_APPS` setting, so find it in your `settings.py` file.

To setup up a normal minimal set up of django-health-check add this to your
`INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... your existing apps stay here ...
    'health_check',
    'health_check.db',
    'health_check.cache',
]
```

This will include checking of both your database and cache subsystems are working
and available.

{% callout title="NOTE!" %}
The first entry, `health_check`, is needed even if you do not plan to use any of the included
health checks and only plan to use ones you have written. This is how
the system loads and runs all other health checks.
{% /callout %}

