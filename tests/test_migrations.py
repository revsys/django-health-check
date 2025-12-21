from unittest.mock import patch

import pytest
from django.db.migrations import Migration

from health_check.contrib.migrations.backends import MigrationsHealthCheck


class MockMigration(Migration): ...


class TestMigrationsHealthCheck:
    @pytest.mark.django_db
    def test_check_status_work(self):
        with patch(
            "health_check.contrib.migrations.backends.MigrationsHealthCheck.get_migration_plan",
            return_value=[],
        ):
            backend = MigrationsHealthCheck()
            backend.run_check()
            assert not backend.errors

    @pytest.mark.django_db
    def test_check_status_raises_error_if_there_are_migrations(self):
        with patch(
            "health_check.contrib.migrations.backends.MigrationsHealthCheck.get_migration_plan",
            return_value=[(MockMigration, False)],
        ):
            backend = MigrationsHealthCheck()
            backend.run_check()
            assert backend.errors
