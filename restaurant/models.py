from django.db import models


class Restaurant(models.Model):
    yandex_id = models.PositiveBigIntegerField()
    company = models.CharField(max_length=1)
    region = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

