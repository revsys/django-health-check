# -*- coding: utf-8 -*-
from django.conf import settings

from health_check.plugins import plugin_dir
from .base import StorageHealthCheck


class DefaultFileStorageHealthCheck(StorageHealthCheck):
    storage = settings.DEFAULT_FILE_STORAGE


plugin_dir.register(DefaultFileStorageHealthCheck)
