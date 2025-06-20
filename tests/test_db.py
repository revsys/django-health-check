from unittest.mock import patch

from django.db import DatabaseError, IntegrityError
from django.db.models import Model
from django.test import TestCase

from health_check.db.backends import DatabaseBackend
from health_check.mixins import CheckMixin


class MockDBModel(Model):
    """
    A Mock database used for testing.

    error_thrown - The Exception to be raised when save() is called, if any.
    """

    error_thrown = None

    def __init__(self, error_thrown=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    @patch(
        "health_check.db.backends.TestModel.objects.create",
        lambda title=None: MockDBModel(),
    )
    def test_check_status_works(self):
        db_backend = DatabaseBackend()
        db_backend.check_status()
        self.assertFalse(db_backend.errors)

    @patch(
        "health_check.db.backends.TestModel.objects.create",
        lambda title=None: raise_(IntegrityError),
    )
    def test_raise_integrity_error(self):
        db_backend = DatabaseBackend()
        db_backend.run_check()
        self.assertTrue(db_backend.errors)
        self.assertIn("unexpected result: Integrity Error", db_backend.pretty_status())

    @patch(
        "health_check.db.backends.TestModel.objects.create",
        lambda title=None: MockDBModel(error_thrown=DatabaseError),
    )
    def test_raise_database_error(self):
        db_backend = DatabaseBackend()
        db_backend.run_check()
        self.assertTrue(db_backend.errors)
        self.assertIn("unavailable: Database error", db_backend.pretty_status())

    @patch(
        "health_check.db.backends.TestModel.objects.create",
        lambda title=None: MockDBModel(error_thrown=Exception),
    )
    def test_raise_exception(self):
        db_backend = DatabaseBackend()
        with self.assertRaises(Exception):
            db_backend.run_check()


class MultipleDatabasesTests(TestCase):
    """Ensures all databases are registered as their own backend and each backend runs in its own database."""

    def test_all_databases_registered(self):
        check_mixin = CheckMixin()
        all_plugins = check_mixin.plugins

        self.assertIn("DatabaseBackend[default]", all_plugins)
        self.assertIn("DatabaseBackend[other]", all_plugins)

    @patch("django.db.transaction.atomic")
    def test_checks_on_database(self, mocked_atomic):
        db1_health_check = DatabaseBackend(database_name="other")

        db1_health_check.run_check()

        mocked_atomic.assert_called_with(using="other")
