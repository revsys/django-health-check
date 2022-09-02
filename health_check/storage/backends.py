import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import get_storage_class

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable


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
        if isinstance(self.storage, str):
            return get_storage_class(self.storage)()
        else:
            return self.storage

    def get_file_name(self):
        return "health_check_storage_test/test-%s.txt" % uuid.uuid4()

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
        except Exception as e:
            raise ServiceUnavailable("Unknown exception") from e


class DefaultFileStorageHealthCheck(StorageHealthCheck):
    storage = settings.DEFAULT_FILE_STORAGE
