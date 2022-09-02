import django

if django.VERSION < (3, 2):
    default_app_config = "health_check.contrib.celery_ping.apps.HealthCheckConfig"
