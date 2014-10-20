from django.db import models


class TestModel(models.Model):
    title = models.CharField(max_length=128)
