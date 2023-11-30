---
title:  Disk and memory usage Health Check
pageTitle: django-health-check psutil check
description:  Checks the disk usage and memory usage of the application
---
The `health_check.contrib.psutil` uses the `psutil` library to to gather information
on the memory and disk usage of the application.

Ensure you have [ `psutil`](https://psutil.readthedocs.io/en/latest/#id1) installed.


## Settings

The disk and memory usage have a default setting:
```python
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN' = 100,    # in MB
}
```
They can be adjusted to the needs of the application. In case you want to disable the 
above fields, set the value to `None`

## What does it check?

This check does the following:

- Collect data on the current resource
- Compare collected data to the predefined threshold

This check allows administrators to take proactive measures like resource allocation adjustments,
to maintain a healthy operating environment. Additionally, full disks and out-of-memory conditions are common causes of service outages.
These situations can be averted by checking disk and memory utilization via the psutil package.

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
 
3.Add the `health_check.contrib.psutil` applications 
to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'health_check',                             
    'health_check.contrib.psutil',
]

HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN' = 100,    # in MB
}

```
4.Run the health check
```shell
python manage.py health_check

```

