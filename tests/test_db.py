from unittest.mock import patch

from django.db import DatabaseError, IntegrityError
from django.db.models import Model
from django.test import TestCase, override_settings

from health_check.db.apps import HealthCheckConfig
from health_check.db.backends import DatabaseBackend
from health_check.mixins import CheckMixin
from health_check.plugins import plugin_dir

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

    @patch("django.db.transaction.atomic")
    def test_checks_on_database(self, mocked_atomic):
        """The backend should use the correct database alias when checking."""
        db1_health_check = DatabaseBackend(database_name="other")
        db1_health_check.run_check()
        mocked_atomic.assert_called_with(using="other")

class HealthCheckRegistrationTests(TestCase):
    """Test the dynamic registration of database health checks."""

    def setUp(self):
        """Reset the plugin directory before each test."""
        plugin_dir.reset()
        self.app_config = HealthCheckConfig()

    def tearDown(self):
        """Ensure the plugin directory is clean after tests."""
        plugin_dir.reset()

    @override_settings(
        DATABASES={"default": {}, "other": {}},
        HEALTH_CHECK={},
    )
    def test_registers_all_databases_by_default(self):
        """If HEALTH_CHECK is not set, all databases should be registered."""
        self.app_config.ready()
        self.assertIn("DatabaseBackend[default]", plugin_dir._registry)
        self.assertIn("DatabaseBackend[other]", plugin_dir._registry)
        self.assertEqual(len(plugin_dir._registry), 2)

    @override_settings(
        DATABASES={"default": {}, "insights": {}, "ignored_db": {}},
        HEALTH_CHECK={
            "SUBSETS": {
                "database-probe": [
                    "DatabaseBackend[default]",  # Test parsing format
                    "insights",  # Test plain string format
                ],
            },
        },
    )
    def test_registers_only_probed_databases(self):
        """If database-probe is set, only specified databases should be registered."""
        self.app_config.ready()
        self.assertIn("DatabaseBackend[default]", plugin_dir._registry)
        self.assertIn("DatabaseBackend[insights]", plugin_dir._registry)
        self.assertNotIn("DatabaseBackend[ignored_db]", plugin_dir._registry)
        self.assertEqual(len(plugin_dir._registry), 2)

    @override_settings(
        DATABASES={"default": {}},
        HEALTH_CHECK={
            "SUBSETS": {
                "database-probe": ["DatabaseBackend[default]", "non_existent_db"]
            }
        },
    )
    def test_ignores_non_existent_databases_in_probe_list(self):
        """Registration should not fail or register a check for a DB not in settings."""
        self.app_config.ready()
        self.assertIn("DatabaseBackend[default]", plugin_dir._registry)
        self.assertNotIn("DatabaseBackend[non_existent_db]", plugin_dir._registry)
        self.assertEqual(len(plugin_dir._registry), 1)

    @override_settings(
        DATABASES={"default": {}, "other": {}},
        HEALTH_CHECK={"SUBSETS": {"database-probe": []}},
    )
    def test_registers_no_databases_for_empty_probe_list(self):
        """If the probe list is empty, no database checks should be registered."""
        self.app_config.ready()
        self.assertEqual(len(plugin_dir._registry), 0)
