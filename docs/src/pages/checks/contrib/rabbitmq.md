---
title: RabbitMQ Health Check
pageTitle: django-health-check rabbitmq check
description: Verifies that the RabbitMQ service is healthy and responsive
---

The `health_check.contrib.rabbitmq` verifies that the RabbitMQ service is healthy and responsive.

Ensure that you have [RabbitMQ](https://pypi.org/project/rabbitmq/) installed.


## Settings

The setting that needs to be correct is `BROKER_URL` in your `settings.py` to connect to your Rabbit server.  

```python 
BROKER_URL = "amqp://myuser:mypassword@localhost:5672/myvhost"
```

## What does it check?

This check does the following:

- Retrieves the Broker URL
- Establish connection to the RabbitMQ broker 
- Opens channel for connection and checks if new channels can be created

Through performing this checks, potential issues with RabbitMQ are identified and corrective action taken to
maintain health and stability of the application.


## Steps
1.Installation
 ```shell
#requirements.txt
django-health-check == x.x.x
```

2.Configure your health check URL endpoint:

```python
urlpatterns = [
    # ... your existing URLs here ...
    url(r'^health/', include('health_check.urls')),
]
```

3.Add the `health_check.contrib.rabbitmq` applications to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'health_check',                             
    'health_check.contrib.rabbitmq',
',
]

BROKER_URL = "amqp://myuser:mypassword@localhost:5672/myvhost"

```

4.Run the health check
```shell
python manage.py health_check

```