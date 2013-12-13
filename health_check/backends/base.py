from django.core.files.storage import get_storage_class
from django.core.files.base import ContentFile
import datetime
import random

class HealthCheckStatusType(object):
    unavailable = 0
    working = 1
    unexpected_result = 2

HEALTH_CHECK_STATUS_TYPE_TRANSLATOR = {
    0: "unavailable",
    1: "working",
    2: "unexpected result",
}


class HealthCheckException(Exception):
    pass


class ServiceUnavailable(HealthCheckException):
    message = HEALTH_CHECK_STATUS_TYPE_TRANSLATOR[0]
    code = 0


class ServiceReturnedUnexpectedResult(HealthCheckException):
    message = HEALTH_CHECK_STATUS_TYPE_TRANSLATOR[2]
    code = 2


class BaseHealthCheckBackend(object):

    def check_status(self):
        return None

    @property
    def status(self):
        if not getattr(self, "_status", False):
            try:
                setattr(self, "_status", self.check_status())
            except (ServiceUnavailable, ServiceReturnedUnexpectedResult) as e:
                setattr(self, "_status", e.code)

        return self._status

    def pretty_status(self):
        return u"%s" % (HEALTH_CHECK_STATUS_TYPE_TRANSLATOR[self.status])

    @classmethod
    def identifier(cls):
        return cls.__name__


class StorageHealthCheck(BaseHealthCheckBackend):
    """
    Tests the status of a StorageBakcend. Can be extended to test any storage backend by subclassing:

        class MyStorageHealthCheck(StorageHealthCheck):
            storage = 'some.other.StorageBackend'
        plugin_dir.register(MyStorageHealthCheck)

    storage must be either a string pointing to a storage class (e.g 'django.core.files.storage.FileSystemStorage') or
    a Storage instance.
    """
    storage = None

    def get_storage(self):
        if isinstance(self.storage, basestring):
            return get_storage_class(self.storage)()
        else:
            return self.storage

    def get_file_name(self):
        return 'health_check_storage_test/test-%s-%s.txt' % (datetime.datetime.now(), random.randint(10000,99999))

    def get_file_content(self):
        return 'this is the healthtest file content'

    def check_status(self):
        try:
            # write the file to the storage backend
            storage = self.get_storage()
            file_name = self.get_file_name()
            file_content = self.get_file_content()

            # save the file
            file_name = storage.save(file_name, ContentFile(content=file_content))
            # read the file and compare
            f = storage.open(file_name)
            if not storage.exists(file_name):
                raise ServiceUnavailable("File does not exist")
            if not f.read() == file_content:
                raise ServiceUnavailable("File content doesn't match")
            # delete the file and make sure it is gone
            storage.delete(file_name)
            if storage.exists(file_name):
                raise ServiceUnavailable("File was not deleted")
            return True
        except Exception, e:
            raise ServiceUnavailable("Unknown exception")