---
title: Included Health Checks
pageTitle: django-health-check - List of included health checks
description: List of all health checks that come included with django-health-check
---

## Standard Health Checks

The standard health checks basically any well run Django project should
include are:

- [health_check](/checks/main) is required to be listed to run the other checks
- [health_check.db](/checks/db) verify you can read/write to your database
- [health_check.cache](/checks/cache) check your cache backend
- [health_check.storage](/checks/storage) check your file storage backend

## Contrib Health Checks

All of these were included in a contrib package historically.  We plan to
fold these into the main list of packages in a future release.  Their Python
path's all begin with `health_check.contrib.`

- [migrations](/checks/contrib/migrations) check your Django migrations
- [celery](/checks/contrib/celery) validate Celery is working properly
- [celery_ping](/checks/contrib/celery_ping) validate Celery is working properly
- [psutil](/checks/contrib/psutil) checks disk and memory utiization
- [s3boto3_storage](/checks/contrib/s3boto3_storage) checks s3boto3_storage if using S3 and django-storages
- [rabbitmq](/checks/contrib/rabbitmq) verifies rabbitmq is happily munching on carrots
- [redis](/checks/contrib/redis) checks you can read/write to Redis