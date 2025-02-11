from django.apps import AppConfig

from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    name = "health_check.contrib.db_heartbeat"

    def ready(self):
        from .backends import DatabaseHeartBeatCheck

        plugin_dir.register(DatabaseHeartBeatCheck)
