Settings
========

Settings can be configured via the ``HEALTH_CHECK`` dictionary.

``psutil``
----------

The following default settings will be used to check for disk and memory
utilization. If you would prefer different thresholds, you can add the dictionary
below to your Django settings file and adjust the values accordingly. If you want
to disable any of these checks, set its value to ``None``.

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
