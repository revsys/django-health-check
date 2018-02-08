contrib
=======

``psutil``
----------

Full disks and out-of-memory conditions are common causes of service outages.
These situations can be averted by checking disk and memory utilization via the
``psutil`` package:

.. code::

    pip install psutil

Once that dependency has been installed, make sure that the corresponding Django
app has been added to ``INSTALLED_APPS``:

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
