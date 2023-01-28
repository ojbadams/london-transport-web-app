""" Models.py """
from django.db import models

# Create your models here.

class BikePointLocation(models.Model):
    """ Bike Point Model """
    common_name = models.CharField(max_length=200)
    lat = models.FloatField()
    lon = models.FloatField()
    id = models.IntegerField(primary_key=True)

