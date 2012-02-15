from django.db import models

class Location(models.Model):
    country = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    
    # Optional
    lat = models.CharField(max_length=50)
    lng = models.CharField(max_length=50)