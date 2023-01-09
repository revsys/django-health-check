---
title: Getting started
pageTitle: django-health-check Documentation
description: Don't just check the port is open, check that it works.  django-health-check tests that you can read and write to your DB, that your cache is working, Celery, or you can even write your own health checks.
---

Learn how to setup up django-health-check and write your own custom health checks {% .lead %}

{% quick-links %}

{% quick-link title="Installation" icon="installation" href="/install" description="Step-by-step guides to installing the library." /%}

{% quick-link title="What are health checks?" icon="presets" href="/why" description="Learn why health checks are so important to a well run Django app." /%}

{% quick-link title="Write your own checks" icon="plugins" href="/writing-your-own-checks" description="How to write your own health checks for Django." /%}

{% quick-link title="Included Health Checks" icon="theming" href="/checks" description="All of the standard and contrib checks included." /%}
{% /quick-links %}

Possimus saepe veritatis sint nobis et quam eos. Architecto consequatur odit perferendis fuga eveniet possimus rerum cumque. Ea deleniti voluptatum deserunt voluptatibus ut non iste.

---

## Quick start

Getting started with django-health-check is easy, but don't dismiss the power of writing your own health checks.

### Installing django-health-check

To install django-health-check you need to use pip.

```shell
pip install django-health-check
```

You should preferably pin this dependency to the specific version in your pip requirements like this:

```
# requirements.txt
django-health-check==3.17.0
```

Once it is installed you need to add the checks you want to use to your Django settings. Find
your settings.py file and add these to your `INSTALLED_APPS`.

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
both the standard and contrib modules.  Ideally, you would write custom checks
for all of the services your application needs to function properly.

Does your app use Celery? Then you should use the Celery related checks.  Are
you using Redis? Then you should use the Redis check.

Using something not covered in the library like Kafka? You should [write your
own health checks](/writing-your-own-checks) that verify you can interact with Kafka the way your app needs.