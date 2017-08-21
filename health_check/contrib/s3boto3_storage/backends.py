import logging

from health_check.storage.backends import StorageHealthCheck


class S3Boto3StorageHealthCheck(StorageHealthCheck):
    """
    Tests the status of a `S3BotoStorage` file storage backend.

    S3BotoStorage is included in the `django-storages` package
    and recommended by for example Amazon and Heroku for Django
    static and media file storage on cloud platforms.

    ``django-storages`` can be found at https://git.io/v1lGx
    ``S3Boto3Storage`` can be found at
        https://github.com/jschneier/django-storages/blob/master/storages/backends/s3boto3.py
    """

    logger = logging.getLogger(__name__)
    storage = 'storages.backends.s3boto3.S3Boto3Storage'

    def check_delete(self, file_name):
        storage = self.get_storage()
        storage.delete(file_name)
