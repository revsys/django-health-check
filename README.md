django-health-check
==================

This project checks a number of backends, if they are able to connect and do a simple action, e.g. check out the django ORM backend:


```python

class DjangoDatabaseBackend(BaseHealthCheckBackend):

    def check_status(self):
        try:
            obj = TestModel.objects.create(title="test")
            obj.title = "newtest"
            obj.save()
            obj.delete()
            return HealthCheckStatusType.working
        except IntegrityError:
            return HealthCheckStatusType.unexpected_result
        except DatabaseError:
            return HealthCheckStatusType.unavailable

```

The project is made using some of the same codes, that the django admin site uses - so when you have sucessfully written a new plugin, you register it to the pool, e.g. 

```python
plugin_dir.register(DjangoDatabaseBackend)
```


Installing
==========

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
(remember to add dependencies, e.g. djcelery - however you should have that already, if you have celery running)
