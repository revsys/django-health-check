from django.db import models


class TestModel(models.Model):
    title = models.CharField(max_length=128)

    class Meta:
        db_table = "health_check_db_testmodel"
