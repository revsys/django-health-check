from celery import Celery

app = Celery('testapp')
app.config_from_object('django.conf:settings', namespace='CELERY')
