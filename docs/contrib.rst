contrib
=======

`psutil`
--------

Full disks and out-of-memory conditions are common causes of service outages.
These situations can be averted by checking disk and memory utilization via the
`psutil` package:

.. code::

    pip install psutil

Once that dependency has been installed, make sure that the corresponding Django
app has been added to `INSTALLED_APPS`:

.. code:: python

    INSTALLED_APPS = [
        # ...
        'health_check',                             # required
        'health_check.contrib.psutil',              # disk and memory utilization; requires psutil
        # ...
    ]

The following default settings will be used to check for disk and memory
utilization. If you would prefer different thresholds, you can add the dictionary
below to your Django settings file and adjust the values accordingly. If you want
to disable any of these checks, set its value to ``None``.

.. code:: python

    HEALTH_CHECK = {
        'DISK_USAGE_MAX': 90,  # percent
        'MEMORY_MIN' = 100,    # in MB
    }

`celery`
--------

If you are using Celery you may choose between two different Celery checks.

`health_check.contrib.celery` sends a task to the queue and it expects that task
to be executed in `HEALTHCHECK_CELERY_TIMEOUT` seconds which by default is three seconds.
The task is sent with a priority of `HEALTHCHECK_CELERY_PRIORITY` (default priority by default).
You may override that in your Django settings module. This check is suitable for use cases
which require that tasks can be processed frequently all the time.

`health_check.contrib.celery_ping` is a different check. It checks that each predefined
Celery task queue has a consumer (i.e. worker) that responds `{"ok": "pong"}` in
`HEALTHCHECK_CELERY_PING_TIMEOUT` seconds. The default for this is one second.
You may override that in your Django settings module. This check is suitable for use cases
which don't require that tasks are executed almost instantly but require that they are going
to be executed in sometime the future i.e. that the worker process is alive and processing tasks
all the time.

You may also use both of them. To use these checks add them to `INSTALLED_APPS` in your
Django settings module.
