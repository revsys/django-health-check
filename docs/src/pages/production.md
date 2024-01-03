---
title: Production Considerations
pageTitle: Production Considerations for django-health-check
description: Using django-health-check in production has a few small things to consider.
---

Each health check you add determines if that subsystem is up and running.

For example, `health_check.db` creates a new row in the database,
updates it's value, and then deletes it. This runs three SQL queries
against your database. Similarly, `health_check.cache` sets a value in your
cache backend and then retrieves it again, verifying that the value matches.

While none of these checks on their own do a **LOT** of work, it is still work.
The tasks take time and it's easy to have a combination of tests that take
many seconds to complete.  Perhaps even going over the default timeouts you
have setup for your [WSGI](https://wsgi.readthedocs.io/en/latest/what.html) and/or [webserver](https://www.digitalocean.com/community/conceptual-articles/introduction-to-web-servers).

You can solve this by increasing your timeouts, but there is another
issue.

## Possible Denial of Service (DoS) Attack

Your health checks can be used as a potential *denial of service* attack
vector.

Imagine your health checks take 10 seconds to complete.
An attacker can spawn a thousand threads and ask for a thousand health checks at
once effectively overloading your Django app with health requests.

### Non-public health checks

The way around this is to **NOT** expose the health check URL
to the public Internet.  You can do this by restricting access with
nginx (or whichever [webserver](https://www.digitalocean.com/community/conceptual-articles/introduction-to-web-servers) you are using in front of your Django [WSGI](https://wsgi.readthedocs.io/en/latest/what.html) process).

Another option is to make your health check endpoint unguessable.  So
instead of:

```python
# Easily guessable
urlpatterns = [
    url(r'^health/', include('health_check.urls')),
]
```

make it something like:

```python
urlpatterns = [
    url(r'^secret-health-thing/', include('health_check.urls')),
]
```

This reduces the chances of an attacker or even a simple spidering web bot
to overload your app doing health checks.
