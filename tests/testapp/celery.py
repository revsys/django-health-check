from celery import Celery

app = Celery("testapp", broker="memory://")
app.config_from_object("django.conf:settings", namespace="CELERY")
