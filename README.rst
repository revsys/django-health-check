django-health-check
===================

|version| |ci| |coverage| |health| |license|

This project checks the health for a number of backends and sees if they are able
to connect and do a simple action. For example, check out the Django ORM backend:

.. code:: python

    class DjangoDatabaseBackend(BaseHealthCheckBackend):
        def check_status(self):
            try:
                obj = TestModel.objects.create(title="test")
                obj.title = "newtest"
                obj.save()
                obj.delete()
                return True
            except IntegrityError:
                raise ServiceReturnedUnexpectedResult("Integrity Error")
            except DatabaseError:
                raise ServiceUnavailable("Database error")

The project is made using some of the same plugin code that the Django
admin site uses - so when you have successfully written a new plugin, you
register it to the pool, e.g.

.. code:: python

    plugin_dir.register(DjangoDatabaseBackend)

Install
=======

Add this to urls.py

.. code:: python

    url(r'^ht/', include('health_check.urls'))

Add required apps:

.. code:: python

        'health_check',
        'health_check_celery',
        'health_check_db',
        'health_check_cache',
        'health_check_storage',

Remember to add dependencies, for example ``djcelery`` for Celery. You should have
that already, if you have Celery running. You'll also have to make sure
that you have a `result backend`_ configured.

.. _result backend: http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#keeping-results

If you are using Celery 3, use the ``health_check_celery3``
application instead of ``health_check_celery``.

Set up monitoring
=================

E.g. add to pingdom - django-health-check will return HTTP 200 if
everything is OK and HTTP 500 if *anything* is not working.

Dependencies
============

Django 1.4+

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
