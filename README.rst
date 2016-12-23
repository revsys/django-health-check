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

Celery notes
~~~~~~~~~~~~

If you are using current Celery (version 3 or 4) the ``health_check_celery`` application should work out of the box.

This package also offers a ``health_check_celery2`` application for Celery 2 support and backwards compatibility. ``health_check_celery2`` was previously named ``health_check_celery``.

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
