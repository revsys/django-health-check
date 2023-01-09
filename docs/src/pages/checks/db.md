---
title: Database Health Check
pageTitle: django-health-check database check
description: Verify your Django application is able to communicate with the database server
---

The `health_check.db` health check verifies that both Django and your database
server are both configured properly and functioning properly.

## Settings

The only settings that need to be correct are the standard Django `DATABASES`
settings in your `settings.py`.

## What does it check?

This check specifically does the following:

- It creates a new row in a Django ORM model for this app
- It then updates that row with a new value
- It then deletes the row

This ensures your app can communicate with the database and that it's able to
write new rows.

The idea being if you can write and update a row in a specific Django model
your app can most likely read and write rows to any of it's models without
issue.