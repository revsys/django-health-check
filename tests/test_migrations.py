from unittest.mock import patch

from django.db.migrations import Migration
from django.test import TestCase

from health_check.contrib.migrations.backends import MigrationsHealthCheck


class MockMigration(Migration):
    ...


class TestMigrationsHealthCheck(TestCase):
    def test_check_status_work(self):
        with patch(
            "health_check.contrib.migrations.backends.MigrationsHealthCheck.get_migration_plan",
            return_value=[],
        ):
            backend = MigrationsHealthCheck()
            backend.run_check()
            self.assertFalse(backend.errors)

    def test_check_status_raises_error_if_there_are_migrations(self):
        with patch(
            "health_check.contrib.migrations.backends.MigrationsHealthCheck.get_migration_plan",
            return_value=[(MockMigration, False)],
        ):
            backend = MigrationsHealthCheck()
            backend.run_check()
            self.assertTrue(backend.errors)
