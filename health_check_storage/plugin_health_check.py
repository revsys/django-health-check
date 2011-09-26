#-*- coding: utf-8 -*-
from health_check.plugins import plugin_dir
from health_check_storage.base import StorageHealthCheck
from django.conf import settings


class DefaultFileStorageHealthCheck(StorageHealthCheck):
    storage = settings.DEFAULT_FILE_STORAGE

plugin_dir.register(DefaultFileStorageHealthCheck)
