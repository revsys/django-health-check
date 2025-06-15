import os
import uuid

from django.conf import settings

from health_check.conf import HEALTH_CHECK
from django.core.files.base import ContentFile
from django.core.files.storage import InvalidStorageError, default_storage, storages

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable

STORAGE_DIR = HEALTH_CHECK["STORAGE_DIR"]


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

    storage_alias = None
    storage = None

    def get_storage(self):
        try:
            return storages[self.storage_alias]
        except InvalidStorageError:
            return None

    def get_file_name(self):
        """Return a unique file name for the health check.

        It needs to be a relative path to the storage directory to ensure
        that the file can be created in the storage backend."""
        relative_file_path = f"health_check_storage_test/test-{uuid.uuid4()}.txt"
        if STORAGE_DIR:
            return os.path.relpath(f"{STORAGE_DIR}/{relative_file_path}", settings.BASE_DIR)
        return relative_file_path

    def get_file_content(self):
        return b"this is the healthtest file content"

    def check_save(self, file_name, file_content):
        storage = self.get_storage()
        # save the file
        file_name = storage.save(file_name, ContentFile(content=file_content))
        # read the file and compare
        if not storage.exists(file_name):
            raise ServiceUnavailable("File does not exist")
        with storage.open(file_name) as f:
            if not f.read() == file_content:
                raise ServiceUnavailable("File content does not match")
        return file_name

    def check_delete(self, file_name):
        storage = self.get_storage()
        # delete the file and make sure it is gone
        storage.delete(file_name)
        if storage.exists(file_name):
            raise ServiceUnavailable("File was not deleted")

    def check_status(self):
        try:
            # write the file to the storage backend
            file_name = self.get_file_name()
            file_content = self.get_file_content()
            file_name = self.check_save(file_name, file_content)
            self.check_delete(file_name)
            return True
        except ServiceUnavailable as e:
            raise e
        except Exception as e:
            raise ServiceUnavailable("Unknown exception") from e


class DefaultFileStorageHealthCheck(StorageHealthCheck):
    storage_alias = "default"
    storage = default_storage
