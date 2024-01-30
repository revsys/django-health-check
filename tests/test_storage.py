import unittest
from unittest import mock

import django
from django.core.files.storage import Storage
from django.test import TestCase

from health_check.exceptions import ServiceUnavailable
from health_check.storage.backends import (
    DefaultFileStorageHealthCheck,
    StorageHealthCheck,
)


class CustomStorage(Storage):
    pass


class MockStorage(Storage):
    """
    A Mock Storage backend used for testing.
    saves - Determines whether save will mock a successful or unsuccessful save
    deletes -  Determines whether save will mock a successful or unsuccessful deletion
    """

    MOCK_FILE_COUNT = 0
    saves = None
    deletes = None

    def __init__(self, saves=True, deletes=True):
        super(MockStorage, self).__init__()
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


def get_file_name(*args, **kwargs):
    return "mockfile.txt"


def get_file_content(*args, **kwargs):
    return b"mockcontent"


@mock.patch(
    "health_check.storage.backends.StorageHealthCheck.get_file_name", get_file_name
)
@mock.patch(
    "health_check.storage.backends.StorageHealthCheck.get_file_content",
    get_file_content,
)
class HealthCheckStorageTests(TestCase):
    """
    Tests health check behavior with a mocked storage backend.
    Ensures check_status returns/raises the expected result when the storage works or raises exceptions.
    """

    def test_get_storage(self):
        """Test get_storage method returns None on the base class, but a Storage instance on default."""
        base_storage = StorageHealthCheck()
        self.assertIsNone(base_storage.get_storage())

        default_storage = DefaultFileStorageHealthCheck()
        self.assertIsInstance(default_storage.get_storage(), Storage)

    @unittest.skipUnless((4, 2) <= django.VERSION < (5, 0), "Only for Django 4.2 - 5.0")
    def test_get_storage_django_between_42_and_50(self):
        """Check that the old DEFAULT_FILE_STORAGE setting keeps being supported."""
        # Note: this test doesn't work on Django<4.2 because the setting value is
        # evaluated when the class attribute DefaultFileStorageHealthCheck.store is
        # read, which is at import time, before we can mock the setting.
        with self.settings(DEFAULT_FILE_STORAGE="tests.test_storage.CustomStorage"):
            default_storage = DefaultFileStorageHealthCheck()
            self.assertIsInstance(default_storage.get_storage(), CustomStorage)

    @unittest.skipUnless((4, 2) <= django.VERSION, "Django 4.2+ required")
    def test_get_storage_django_42_plus(self):
        """Check that the new STORAGES setting is supported."""
        with self.settings(
            STORAGES={"default": {"BACKEND": "tests.test_storage.CustomStorage"}}
        ):
            default_storage = DefaultFileStorageHealthCheck()
            self.assertIsInstance(default_storage.get_storage(), CustomStorage)

    @mock.patch(
        "health_check.storage.backends.DefaultFileStorageHealthCheck.storage",
        MockStorage(),
    )
    def test_check_status_working(self):
        """Test check_status returns True when storage is working properly."""
        default_storage_health = DefaultFileStorageHealthCheck()

        default_storage = default_storage_health.get_storage()

        default_storage_open = "{}.{}.open".format(
            default_storage.__module__, default_storage.__class__.__name__
        )

        with mock.patch(
            default_storage_open,
            mock.mock_open(read_data=default_storage_health.get_file_content()),
        ):
            self.assertTrue(default_storage_health.check_status())

    @unittest.skipUnless(django.VERSION <= (4, 1), "Only for Django 4.1 and earlier")
    @mock.patch(
        "health_check.storage.backends.DefaultFileStorageHealthCheck.storage",
        MockStorage(saves=False),
    )
    def test_file_does_not_exist_django_41_earlier(self):
        """Test check_status raises ServiceUnavailable when file is not saved."""
        default_storage_health = DefaultFileStorageHealthCheck()
        with self.assertRaises(ServiceUnavailable):
            default_storage_health.check_status()

    @unittest.skipUnless((4, 2) <= django.VERSION, "Only for Django 4.2+")
    @mock.patch(
        "health_check.storage.backends.storages",
        {"default": MockStorage(saves=False)},
    )
    def test_file_does_not_exist_django_42_plus(self):
        """Test check_status raises ServiceUnavailable when file is not saved."""
        default_storage_health = DefaultFileStorageHealthCheck()
        with self.assertRaises(ServiceUnavailable):
            default_storage_health.check_status()

    @unittest.skipUnless(django.VERSION <= (4, 1), "Only for Django 4.1 and earlier")
    @mock.patch(
        "health_check.storage.backends.DefaultFileStorageHealthCheck.storage",
        MockStorage(deletes=False),
    )
    def test_file_not_deleted_django_41_earlier(self):
        """Test check_status raises ServiceUnavailable when file is not deleted."""
        default_storage_health = DefaultFileStorageHealthCheck()
        with self.assertRaises(ServiceUnavailable):
            default_storage_health.check_status()

    @unittest.skipUnless((4, 2) <= django.VERSION, "Only for Django 4.2+")
    @mock.patch(
        "health_check.storage.backends.storages",
        {"default": MockStorage(deletes=False)},
    )
    def test_file_not_deleted_django_42_plus(self):
        """Test check_status raises ServiceUnavailable when file is not deleted."""
        default_storage_health = DefaultFileStorageHealthCheck()
        with self.assertRaises(ServiceUnavailable):
            default_storage_health.check_status()
