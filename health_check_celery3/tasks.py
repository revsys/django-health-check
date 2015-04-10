from __future__ import absolute_import

from celery import shared_task


@shared_task(ignore_result=False)
def add(x, y):
    return x + y
