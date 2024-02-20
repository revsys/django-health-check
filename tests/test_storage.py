import unittest
from io import BytesIO
from unittest import mock

import django
from django.core.files.base import File
from django.core.files.storage import Storage
from django.test import TestCase, override_settings

from health_check.contrib.s3boto3_storage.backends import S3Boto3StorageHealthCheck
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


# Mocking the S3Boto3Storage backend
class MockS3Boto3Storage:
    """
    A mock S3Boto3Storage backend to simulate interactions with AWS S3.
    """

    def __init__(self, saves=True, deletes=True):
        self.saves = saves
        self.deletes = deletes
        self.files = {}

    def open(self, name, mode="rb"):
        """
        Simulates opening a file from the mocked S3 storage.
        For simplicity, this doesn't differentiate between read and write modes.
        """
        if name in self.files:
            # Assuming file content is stored as bytes
            file_content = self.files[name]
            if isinstance(file_content, bytes):
                return File(BytesIO(file_content))
            else:
                raise ValueError("File content must be bytes.")
        else:
            raise FileNotFoundError(f"The file {name} does not exist.")

    def save(self, name, content):
        """
        Overriding save to ensure content is stored as bytes in a way compatible with open method.
        Assumes content is either a ContentFile, bytes, or a string that needs conversion.
        """
        if self.saves:
            # Check if content is a ContentFile or similar and read bytes
            if hasattr(content, "read"):
                file_content = content.read()
            elif isinstance(content, bytes):
                file_content = content
            elif isinstance(content, str):
                file_content = content.encode()  # Convert string to bytes
            else:
                raise ValueError("Unsupported file content type.")

            self.files[name] = file_content
            return name
        raise Exception("Failed to save file.")

    def delete(self, name):
        if self.deletes:
            self.files.pop(name, None)
        else:
            raise Exception("Failed to delete file.")

    def exists(self, name):
        return name in self.files


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


@mock.patch("storages.backends.s3boto3.S3Boto3Storage", new=MockS3Boto3Storage)
@override_settings(
    STORAGES={
        "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
    }
)
class HealthCheckS3Boto3StorageTests(TestCase):
    """
    Tests health check behavior with a mocked S3Boto3Storage backend.
    """

    @unittest.skipUnless(django.VERSION <= (4, 1), "Only for Django 4.1 and earlier")
    @mock.patch(
        "storages.backends.s3boto3.S3Boto3Storage",
        MockS3Boto3Storage(deletes=False),
    )
    def test_check_delete_success_django_41_earlier(self):
        """Test that check_delete correctly deletes a file when S3Boto3Storage is working."""
        health_check = S3Boto3StorageHealthCheck()
        mock_storage = health_check.get_storage()
        file_name = "testfile.txt"
        content = BytesIO(b"Test content")
        mock_storage.save(file_name, content)

        with self.assertRaises(ServiceUnavailable):
            health_check.check_delete(file_name)

    @unittest.skipUnless((4, 2) <= django.VERSION, "Only for Django 4.2+")
    def test_check_delete_success(self):
        """Test that check_delete correctly deletes a file when S3Boto3Storage is working."""
        health_check = S3Boto3StorageHealthCheck()
        mock_storage = health_check.get_storage()
        file_name = "testfile.txt"
        content = BytesIO(b"Test content")
        mock_storage.save(file_name, content)

        health_check.check_delete(file_name)
        self.assertFalse(mock_storage.exists(file_name))

    def test_check_delete_failure(self):
        """Test that check_delete raises ServiceUnavailable when deletion fails."""
        with mock.patch.object(
            MockS3Boto3Storage,
            "delete",
            side_effect=Exception("Failed to delete file."),
        ):
            health_check = S3Boto3StorageHealthCheck()
            with self.assertRaises(ServiceUnavailable):
                health_check.check_delete("testfile.txt")

    @unittest.skipUnless(django.VERSION <= (4, 1), "Only for Django 4.1 and earlier")
    @mock.patch(
        "storages.backends.s3boto3.S3Boto3Storage",
        MockS3Boto3Storage(deletes=False),
    )
    def test_check_status_working_django_41_earlier(self):
        """Test check_status returns True when S3Boto3Storage can save and delete files."""
        health_check = S3Boto3StorageHealthCheck()
        with self.assertRaises(ServiceUnavailable):
            self.assertTrue(health_check.check_status())

    @unittest.skipUnless((4, 2) <= django.VERSION, "Only for Django 4.2+")
    def test_check_status_working(self):
        """Test check_status returns True when S3Boto3Storage can save and delete files."""
        health_check = S3Boto3StorageHealthCheck()
        self.assertTrue(health_check.check_status())

    def test_check_status_failure_on_save(self):
        """Test check_status raises ServiceUnavailable when file cannot be saved."""
        with mock.patch.object(
            MockS3Boto3Storage, "save", side_effect=Exception("Failed to save file.")
        ):
            health_check = S3Boto3StorageHealthCheck()
            with self.assertRaises(ServiceUnavailable):
                health_check.check_status()

    def test_check_status_failure_on_delete(self):
        """Test check_status raises ServiceUnavailable when file cannot be deleted."""
        with mock.patch.object(
            MockS3Boto3Storage, "exists", new_callable=mock.PropertyMock
        ) as mock_exists:
            mock_exists.return_value = False
            health_check = S3Boto3StorageHealthCheck()
            with self.assertRaises(ServiceUnavailable):
                health_check.check_status()
