""" Models.py """
from django.db import models

# Create your models here.

class BikePointLocation(models.Model):
    """ Bike Point Model """
    common_name = models.CharField(max_length=200)
    lat = models.FloatField()
    lon = models.FloatField()
    id = models.IntegerField(primary_key=True)

class BikePointCapacity(models.Model):
    """ Model Capacity """
    id = models.IntegerField(primary_key=True)
    capacity = models.IntegerField()
    in_use = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
