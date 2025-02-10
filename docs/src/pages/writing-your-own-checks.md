---
title: Writing custom health checks
pageTitle: Writing custom health checks
description: How to write your own health checks to specifically tests aspects of your system when there isn't a standard or contrib health check already available.
---

Custom Django health checks is necessary for implementing application-specific checks,
monitoring external dependencies, and validating legacy system integrations.

## Template to write custom health checks

Start with this code

```python 

from health_check.backends import BaseHealthCheckBackend

class MyHealthCheckBackend(BaseHealthCheckBackend):
    #: The status endpoints will respond with a 200 status code
    #: even if the check errors.
    critical_service = False

    def check_status(self):
        # The test code goes here.
        # You can use `self.add_error` or
        # raise a `HealthCheckException`,
        # similar to Django's form validation.
        pass

    def identifier(self):
        return self.__class__.__name__  # Display name on the endpoint.
```

After writing a custom checker, register it in your app configuration:

```python
from django.apps import AppConfig

from health_check.plugins import plugin_dir

class MyAppConfig(AppConfig):
    name = 'my_app'

    def ready(self):
        from .backends import MyHealthCheckBackend
        plugin_dir.register(MyHealthCheckBackend)

```

***Note:***
The application you write the checker into should already be registered in your `INSTALLED_APPS`.

Remember to adapt the code based on your specific application requirements and the type of health check you want to perform. 