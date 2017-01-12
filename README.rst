===================
django-health-check
===================

|version| |ci| |coverage| |health| |license|

This project checks the health for a number of backends and sees if they are able
to connect and do a simple action.

.. code:: python

    plugin_dir.register(DjangoDatabaseBackend)

Install
-------

Add this to urls.py

.. code:: python

    url(r'^ht/$', include('health_check.urls'))

Add required apps:

.. code:: python

        'health_check',  # required
        'health_check.db',
        'health_check.cache',
        'health_check.storage',
        'health_check.contrib.celery',
        'health_check.contrib.s3boto_storage',

.. Note:: Not that you will need a result backend configured for celery.

Set up monitoring
-----------------

You can use tools like Pingdom_ or other uptime robots.
The ``/ht/`` endpoint will respond a HTTP 200 if all checks passed
and a HTTP 500 if any of the tests failed.

Writing a custom health check
-----------------------------

Writing a health check:

.. code:: python

    class MyHealthCheckBackend(BaseHealthCheckBackend):
        def check_status(self):
            # The test code goes here.
            # You can use `self.add_error` or raise a
            # `HealthCheckException`. Similar to Django's form validation.
            pass

        def identifier(self):
            return self.__class__.__name__  # Display name on the endpoint.

Register the backend in your app configuration:

.. code:: python

    from django.apps import AppConfig

    from health_check.plugins import plugin_dir


    class MyAppConfig(AppConfig):
        name = 'my_app'

        def ready(self):
            from .backends import MyHealthCheckBackend
            plugin_dir.register(MyHealthCheckBackend)


.. |version| image:: https://img.shields.io/pypi/v/django-health-check.svg
   :target: https://pypi.python.org/pypi/django-health-check/
.. |ci| image:: https://api.travis-ci.org/KristianOellegaard/django-health-check.svg?branch=master
   :target: https://travis-ci.org/KristianOellegaard/django-health-check
.. |coverage| image:: https://coveralls.io/repos/KristianOellegaard/django-health-check/badge.svg?branch=master
   :target: https://coveralls.io/r/KristianOellegaard/django-health-check
.. |health| image:: https://landscape.io/github/KristianOellegaard/django-health-check/master/landscape.svg?style=flat
   :target: https://landscape.io/github/KristianOellegaard/django-health-check/master
.. |license| image:: https://img.shields.io/badge/license-BSD-blue.svg
   :target: LICENSE

.. _Pingdom: https://www.pingdom.com/
