---
title:  S3boto Storage Health Check
pageTitle: django-health-check S3boto3 Storage check
description: Checks to ensure the storage backend is functioning correctly
---
The `health_check.contrib.s3boto3_storage` uses the `boto3` library to interact with AWS 
S3 and perform a series of checks to ensure the storage backend is functioning correctly.
 
Ensure you have installed [`boto3`](https://pypi.org/project/boto3/).

For cloud-based static and media file storage on platforms like Amazon and Heroku, the recommended backend is 
[S3BotoStorage](https://github.com/jschneier/django-storages/blob/master/storages/backends/s3boto3.py), 
which is part of [`django-storages`](https://git.io/v1lGx) package. 

**Note:** 
If you are using `boto 2.x.x` use `health_check.contrib.s3boto_storage`


## What does it check?

This check does the following:

- Tests the status of an Amazon S3 storage backend 
- Tests the ability to delete a file from the S3 storage.

This check  ensures that the storage backend is functioning properly and that files can be removed from S3 storage
when needed.

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
 
3.Add the `health_check.contrib.s3boto3_storage` applications 
to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'health_check',                             
    'health_check.contrib.s3boto3_storage',
]
```
4.Run the health check
```shell
python manage.py health_check

```

