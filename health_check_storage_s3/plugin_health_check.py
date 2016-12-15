# -*- coding: utf-8 -*-
import logging

from health_check.plugins import plugin_dir
from health_check_storage.base import StorageHealthCheck


class S3BotoStorageHealthCheck(StorageHealthCheck):
    """
    Tests the status of a `S3BotoStorage` file storage backend.

    S3BotoStorage is included in the `django-storages` package
    and recommended by for example Amazon and Heroku for Django
    static and media file storage on cloud platforms.

    ``django-storages`` can be found at https://git.io/v1lGx
    ``S3BotoStorage`` can be found at https://git.io/v1lGF
    """

    logger = logging.getLogger(__name__)
    storage = 'storages.backends.s3boto.S3BotoStorage'

    def check_delete(self, file_name):
        storage = self.get_storage()
        storage.delete(file_name)

plugin_dir.register(S3BotoStorageHealthCheck)
