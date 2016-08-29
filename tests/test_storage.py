from django.core.files.base import File
from django.core.files.storage import Storage
from django.test import TestCase

from health_check.backends.base import ServiceUnavailable
from health_check_storage.base import StorageHealthCheck
from health_check_storage.plugin_health_check import \
    DefaultFileStorageHealthCheck
from mock import MagicMock, patch


# A mock version of the base Storage Backend class
class MockStorage(Storage):
    MOCK_FILE_COUNT = 0
    saves = None  # Determines whether save will mock a successful or unsuccessful save
    deletes = None  # Determines whether save will mock a successful or unsuccessful deletion

    def __init__(self, saves=True, deletes=True):
        self.MOCK_FILE_COUNT = 0
        self.saves = saves
        self.deletes = deletes

    def exists(self, file_name):
        return self.MOCK_FILE_COUNT != 0

    def delete(self, name):
        if self.deletes:
            self.MOCK_FILE_COUNT -= 1

    def save(self, name, content, max_length=None):
        if self.saves:
            self.MOCK_FILE_COUNT += 1

    def open(self, name, mode='rb'):
        return MagicMock(spec=File, name='mockfile.txt', read=lambda: b'this is the healthtest file content')


def mock_file_name(file):
    return 'mockfile.txt'


@patch("health_check_storage.base.StorageHealthCheck.get_file_name", mock_file_name)
class HealthCheckStorageTests(TestCase):

    # Test that the get_storage method returns None on the base class, but a Storage instance on default
    def test_get_storage(self):
        base_storage = StorageHealthCheck()
        self.assertIsNone(base_storage.get_storage())
        default_storage = DefaultFileStorageHealthCheck()
        self.assertIsInstance(default_storage.get_storage(), Storage)

    # Test that check status returns true when storage is working properly
    @patch("health_check_storage.plugin_health_check.DefaultFileStorageHealthCheck.storage",
           MockStorage())
    def test_check_status_working(self):
        default_storage = DefaultFileStorageHealthCheck()
        self.assertTrue(default_storage.check_status())

    # Test that check status raises a ServiceUnavailable exception when the file is not saved
    @patch("health_check_storage.plugin_health_check.DefaultFileStorageHealthCheck.storage",
           MockStorage(saves=False))
    def test_file_does_not_exist(self):
        default_storage_health = DefaultFileStorageHealthCheck()
        with self.assertRaises(ServiceUnavailable):
            default_storage_health.check_status()

    # Test that check status raises a ServiceUnavailable exception when the file is not deleted
    @patch("health_check_storage.plugin_health_check.DefaultFileStorageHealthCheck.storage",
           MockStorage(deletes=False))
    def test_file_not_deleted(self):
        default_storage_health = DefaultFileStorageHealthCheck()
        with self.assertRaises(ServiceUnavailable):
            default_storage_health.check_status()
