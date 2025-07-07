import re
from django.apps import AppConfig
from django.conf import settings
from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "health_check.db"

    def ready(self):
        from .backends import DatabaseBackend

        # Helper to extract 'alias' from 'Backend[alias]' or return the string as is
        def extract_db_alias(item_string):
            match = re.search(r'\[(.+?)]', item_string)
            return match.group(1) if match else item_string

        # 1. Get the raw list from settings, defaulting to all DBs.
        raw_probe_list = (
            getattr(settings, "HEALTH_CHECK", {})
            .get("SUBSETS", {})
            .get("database-probe", settings.DATABASES.keys())
        )

        # 2. Parse the raw list into a clean set of DB aliases.
        #    This now correctly handles strings like 'DatabaseBackend[insights]'.
        databases_to_probe = {extract_db_alias(item) for item in raw_probe_list}

        # 3. Register a check for each valid database alias found.
        #    This is cleaner than iterating all dbs and checking for inclusion.
        for db_name in databases_to_probe:
            if db_name in settings.DATABASES:
                plugin_dir.register(DatabaseBackend, database_name=db_name)
