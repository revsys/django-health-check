Settings
========

Settings can be configured via the `HEALTH_CHECK` dictionary.

.. data:: WARNINGS_AS_ERRORS

    Treats :class:`ServiceWarning` as errors, meaning they will cause the views
    to respond with a 500 status code. Default is `True`. If set to
    `False` warnings will be displayed in the template on in the JSON
    response but the status code will remain a 200.

Security
--------

Django health check can be used as a possible DOS attack vector as it can put
your system under a lot of stress. As a default the view is also not cached by
CDNs. Therefore we recommend to use a secure token to protect you application
servers from an attacker.

1.  Setup HTTPS. Seriously...
2.  Add a secure token to your URL.

Create a secure token:

.. code:: shell

    python -c "import secrets; print(secrets.token_urlsafe())"

Add it to your URL:

.. code:: python

    urlpatterns = [
        # ...
        url(r'^ht/super_secret_token/'), include('health_check.urls')),
    ]

You can still use any uptime bot that is URL based while enjoying token protection.

.. warning::
    Do NOT use Django's `SECRET_KEY` setting. This should never be exposed,
    to any third party. Not even your trusted uptime bot.

`cache`
-------

The cache backend uses the following setting:

.. list-table::
   :widths: 25 10 10 55
   :header-rows: 1

   * - Name
     - Type
     - Default
     - Description
   * - `HEALTHCHECK_CACHE_KEY`
     - String
     - `djangohealthcheck_test`
     - Specifies the name of the key to write to and read from to validate that the cache is working.
   * - `HEALTHCHECK_REDIS_URL_OPTIONS`
     - Dict
     - {}
     - Additional arguments which will be passed as keyword arguments to the Redis connection class initialiser.

`psutil`
--------

The following default settings will be used to check for disk and memory
utilization. If you would prefer different thresholds, you can add the dictionary
below to your Django settings file and adjust the values accordingly. If you want
to disable any of these checks, set its value to `None`.

.. code:: python

    HEALTH_CHECK = {
        'DISK_USAGE_MAX': 90,  # percent
        'MEMORY_MIN' = 100,    # in MB
    }

With the above default settings, warnings will be reported when disk utilization
exceeds 90% or available memory drops below 100 MB.

.. data:: DISK_USAGE_MAX

   Specify the desired disk utilization threshold, in percent. When disk usage
   exceeds the specified value, a warning will be reported.

.. data:: MEMORY_MIN

   Specify the desired memory utilization threshold, in megabytes. When available
   memory falls below the specified value, a warning will be reported.

Celery Health Check
-------------------

Using `django.settings` you may exert more fine-grained control over the behavior of the celery health check

.. list-table:: Additional Settings
   :widths: 25 10 10 55
   :header-rows: 1

   * - Name
     - Type
     - Default
     - Description
   * - `HEALTHCHECK_CELERY_QUEUE_TIMEOUT`
     - Number
     - `3`
     - Specifies the maximum amount of time a task may spend in the queue before being automatically revoked with a `TaskRevokedError`.
   * - `HEALTHCHECK_CELERY_RESULT_TIMEOUT`
     - Number
     - `3`
     - Specifies the maximum total time for a task to complete and return a result, including queue time.
   * - `HEALTHCHECK_CELERY_PRIORITY`
     - Number
     - `None`
     - Specifies the healthcheck task priority.
