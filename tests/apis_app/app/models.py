from django.db import models

# Create your models here.
class Airport(models.Model):
    name = models.CharField(max_length=100)
    iata = models.CharField(max_length=3)
    icao = models.CharField(max_length=4)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()
    country = models.CharField(max_length=50)
    desc = models.CharField(max_length=50, blank=True, null=True)
    municipality = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"(Airport) : {self.icao}"
