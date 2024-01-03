---
title: Management Command 
pageTitle: Management  command
description: How to run your  health checks
---

You can run the Django command `health_check` to perform your health checks via the command line, 
or periodically with a cron, as follow:

```shell
python manage.py health_check 
```

This should yield the following output:

```shell
DatabaseHealthCheck      ... working
CustomHealthCheck        ... unavailable: Something went wrong!
```
A critical error will cause the command to quit with the exit code 1.
