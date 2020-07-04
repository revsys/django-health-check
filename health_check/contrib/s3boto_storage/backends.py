import logging

from health_check.conf import HEALTH_CHECK
from health_check.storage.backends import StorageHealthCheck

CRITICAL_S3BOTO_STORAGE = HEALTH_CHECK['CRITICAL_S3BOTO_STORAGE']


class S3BotoStorageHealthCheck(StorageHealthCheck):
    """
    Tests the status of a `S3BotoStorage` file storage backend.

    S3BotoStorage is included in the `django-storages` package
    and recommended by for example Amazon and Heroku for Django
    static and media file storage on cloud platforms.

    ``django-storages`` can be found at https://git.io/v1lGx
    ``S3BotoStorage`` can be found at https://git.io/v1lGF
    """

    critical_service = CRITICAL_S3BOTO_STORAGE

    logger = logging.getLogger(__name__)
    storage = 'storages.backends.s3boto.S3BotoStorage'

    def check_delete(self, file_name):
        storage = self.get_storage()
        storage.delete(file_name)
