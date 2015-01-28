django-health-check
==================

[![version](https://img.shields.io/pypi/v/django-health-check.svg)](https://pypi.python.org/pypi/django-health-check/)
[![ci](https://api.travis-ci.org/KristianOellegaard/django-health-check.svg?branch=master)](https://travis-ci.org/KristianOellegaard/django-health-check)
[![coverage](https://coveralls.io/repos/KristianOellegaard/django-health-check/badge.svg?branch=master)](https://coveralls.io/r/KristianOellegaard/django-health-check)
[![code-health](https://landscape.io/github/KristianOellegaard/django-health-check/master/landscape.svg?style=flat)](https://landscape.io/github/KristianOellegaard/django-health-check/master)
[![BSD License](https://img.shields.io/badge/license-BSD-blue.svg)](LICENSE)

This project checks a number of backends, if they are able to connect and do a simple action, e.g. check out the django ORM backend:


```python

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


```

The project is made using some of the same codes, that the django admin site uses - so when you have sucessfully written a new plugin, you register it to the pool, e.g.

```python
plugin_dir.register(DjangoDatabaseBackend)
```


Install
=======

Add this to urls.py

```python
url(r'^ht/', include('health_check.urls'))
```

Add required apps:

```python
    'health_check',
    'health_check_celery',
    'health_check_db',
    'health_check_cache',
    'health_check_storage',
```
(remember to add dependencies, e.g. djcelery - however you should have that already, if you have celery running).
You'll also have to make sure that you have a
`result backend <http://celery.readthedocs.org/en/latest/configuration.html?highlight=result_backend#std:setting-CELERY_RESULT_BACKEND>`_
configured.
If you are using celery 3, use ``health_check_celery3`` instead of ``health_check_celery``.


Set up monitoring
=================

E.g. add to pingdom - django-health-check will return HTTP 200 if everything is OK and HTTP 500 if *anything* is not working.


Dependencies
============

Django 1.4+

