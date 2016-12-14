from django.db import DatabaseError, IntegrityError
from django.db.models import Model
from django.test import TestCase
from mock import patch

from health_check.backends.base import (
    ServiceReturnedUnexpectedResult, ServiceUnavailable
)
from health_check_db.plugin_health_check import DjangoDatabaseBackend


class MockDBModel(Model):
    """
    A Mock database used for testing.
    error_thrown - The Exception to be raised when save() is called, if any
    """

    error_thrown = None

    def __init__(self, error_thrown=None, *args, **kwargs):
        super(MockDBModel, self).__init__(*args, **kwargs)
        self.error_thrown = error_thrown

    def save(self, *args, **kwargs):
        if self.error_thrown is not None:
            raise self.error_thrown
        else:
            return True

    def delete(self, *args, **kwargs):
        return True


def raise_(ex):
    raise ex


class HealthCheckDatabaseTests(TestCase):
    """
    Tests health check behavior with a mocked database backend.
    Ensures check_status returns/raises the expected result when the database works or raises exceptions.
    """

    @patch('health_check_db.plugin_health_check.TestModel.objects.create',
           lambda title=None: MockDBModel())
    def test_check_status_works(self):
        db_backend = DjangoDatabaseBackend()
        self.assertTrue(db_backend.check_status())

    @patch('health_check_db.plugin_health_check.TestModel.objects.create',
           lambda title=None: raise_(IntegrityError))
    def test_raise_integrity_error(self):
        db_backend = DjangoDatabaseBackend()
        with self.assertRaises(ServiceReturnedUnexpectedResult):
            db_backend.check_status()

    @patch('health_check_db.plugin_health_check.TestModel.objects.create',
           lambda title=None: MockDBModel(error_thrown=DatabaseError))
    def test_raise_database_error(self):
        db_backend = DjangoDatabaseBackend()
        with self.assertRaises(ServiceUnavailable):
            db_backend.check_status()

    @patch('health_check_db.plugin_health_check.TestModel.objects.create',
           lambda title=None: MockDBModel(error_thrown=Exception))
    def test_raise_exception(self):
        db_backend = DjangoDatabaseBackend()
        with self.assertRaises(ServiceUnavailable):
            db_backend.check_status()
