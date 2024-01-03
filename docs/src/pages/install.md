---
title: Installing django-health-check
pageTitle: django-health-check - Installation
description: How to install and set up django-health-check
---

Installing and setting up django-health-check is straight forward.

First, you will need to install the library from [PyPI](https://pypi.org/project/django-health-check/):

```shell
pip install django-health-check
```

Pin the version of the library in your `requirements.txt` to avoid  accidental breaking from a newer version of the library.

```shell
#requirements.txt
django-health-check == x.x.x
```

## Setup the URLs

After installation configure your health check URL endpoint:

```python
urlpatterns = [
    # ... your existing URLs here ...
    url(r'^health/', include('health_check.urls')),
]
```

_*Note, you don't have to call your endpoint `/health/` you could use
`/ht/`, `/_checks/` or any name you prefer.*_

## Configuring checks in Django Settings

To enable individual health checks include them in your
project's `INSTALLED_APPS`  in the `settings.py` file.

To setup up a normal minimal set up of `django-health-check` add this to your
`INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... your existing apps stay here ...
    'health_check',
    'health_check.db',
    'health_check.cache',
]
```

This performs checks for your database and cache subsystems to confirm they are available and working.

{% callout title="NOTE!" %}

The first entry, `health_check`, is needed whether or not you plan to use any of the included
health checks. This is how the system loads and runs all other health checks.

{% /callout %}

