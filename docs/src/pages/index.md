---
title: Getting started
pageTitle: django-health-check Documentation
description: Don't just check if the port is open, check to ensure it works.  django-health-check tests that you can read and write to your DB, that your cache is working, Celery, or you can write your own health checks.
---

Learn how to setup up django-health-check and write your own custom health checks {% .lead %}

{% quick-links %}

{% quick-link title="Installation" icon="installation" href="/install" description="Step-by-step guides to installing the library." /%}

{% quick-link title="What are health checks?" icon="presets" href="/why" description="Learn why health checks are important to a well run Django app." /%}

{% quick-link title="Write your own checks" icon="plugins" href="/writing-your-own-checks" description="How to write your own custom health checks for Django." /%}

{% quick-link title="Included Health Checks" icon="theming" href="/checks" description="All of the standard and contrib checks included." /%}
{% /quick-links %}

---

## Quick start

Getting started with django-health-check is simple, but don't overlook the benefits of writing your own health checks.

### Installing django-health-check

To install `django-health-check` you need to use [pip](https://pypi.org/project/pip/).

```shell
pip install django-health-check
```

Pin this dependency to the specific version in your `requirements.txt` file like this:

```
django-health-check==3.17.0
```

Once installed, add the checks you want to use to your Django settings. In
your `settings.py` file add these in your `INSTALLED_APPS`.

```python
INSTALLED_APPS = [
  # ... your other apps here ...
  'health_check',
  'health_check.db',
]
```

---

## Which checks you should be using?

Depending on your specific Django project, you should include other checks from
both the standard and contrib modules.  Ideally, you should write custom checks
for all of the services your application needs to function properly.

Does your app use Celery? Use the Celery related checks.  Are you using Redis? Use the Redis checks.

If you are using something not covered in the library like Kafka? You should [write your
own health checks](/writing-your-own-checks) to verify that you can interact with Kafka the way your app needs.