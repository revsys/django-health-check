import django

if django.VERSION < (3, 2):
    default_app_config = "health_check.db.apps.HealthCheckConfig"
