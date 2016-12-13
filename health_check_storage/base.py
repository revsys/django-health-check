# -*- coding: utf-8 -*-
import datetime
import random

from django.core.files.base import ContentFile
from django.core.files.storage import get_storage_class
from django.utils.six import string_types

from health_check.backends.base import (
    BaseHealthCheckBackend, HealthCheckException, ServiceUnavailable
)


class StorageHealthCheck(BaseHealthCheckBackend):
    """
    Tests the status of a `StorageBackend`.

    Can be extended to test any storage backend by subclassing:

        class MyStorageHealthCheck(StorageHealthCheck):
            storage = 'some.other.StorageBackend'
        plugin_dir.register(MyStorageHealthCheck)

    storage must be either a string pointing to a storage class
    (e.g 'django.core.files.storage.FileSystemStorage') or a Storage instance.
    """

    storage = None

    def get_storage(self):
        if isinstance(self.storage, string_types):
            return get_storage_class(self.storage)()
        else:
            return self.storage

    def get_file_name(self):
        return 'health_check_storage_test/test-{}-{}.txt'.format(
            datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ'),
            random.randint(10000, 99999)
        )

    def get_file_content(self):
        return b'this is the healthtest file content'

    def check_status(self):
        try:
            # write the file to the storage backend
            storage = self.get_storage()
            file_name = self.get_file_name()
            file_content = self.get_file_content()

            # save the file
            file_name = storage.save(
                file_name, ContentFile(content=file_content)
            )
            if not storage.exists(file_name):
                raise ServiceUnavailable('File does not exist')
            # read the file and compare
            f = storage.open(file_name)
            if not f.read() == file_content:
                raise ServiceUnavailable('File content doesn\'t match')
            # delete the file and make sure it is gone
            storage.delete(file_name)
            if storage.exists(file_name):
                raise ServiceUnavailable('File was not deleted')
            return True
        except HealthCheckException, e:
            raise e
        except Exception:
            raise ServiceUnavailable('Unknown exception')
