---
title: Production Considerations
pageTitle: Production Considerations for django-health-check
description: Using django-health-check in production has a few small things to consider.
---

Each health check you add does some work to determine if that subsystem is up
and running.

For example, `health_check.db` creates a new row in the database,
updates it's value, and then deletes it. This obviously runs three SQL queries
against your database. Similarly, `health_check.cache` sets a value in your
cache backend and then retrives it again, verifying the value matches.

While none of these checks on their own do a **LOT** of work, it is still work.
The tasks take time and it's easy to have a combination of tests that take
many seconds to complete.  Perhaps even going over the default timeouts you
have setup for your WSGI and/or webserver.

You can solve this easily by increasing your timeouts, but there is another
issue.

## Possible Denial of Service (DoS) Attack

Your healh checks can actually be used as a potential *denial of service* attack
vector.

Imagine your health checks take say 10 seconds to complete. It is trivial for
an attacker to spawn a thousand threads and ask for a thousand health checks at
once effectively swamping your Django app with health requests.

### Non-public health checks

The easiest way around this is to just **NOT** expose the health check URL
to the public Internet.  You can do this by actually restricting access with
nginx (or whichever webserver you are using in front of your Django WSGI process).

Another option is to just make your health check endpoint unguessable.  So
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

This greatly reduces the chances of an attacker or even simple web spidering bots
to overload your app doing health checks.
