from django.db import models

class EnergyData(models.Model):
    start_timestamp = models.BigIntegerField()
    end_timestamp = models.BigIntegerField()
    marketprice = models.FloatField()
    unit = models.CharField(max_length=50)
