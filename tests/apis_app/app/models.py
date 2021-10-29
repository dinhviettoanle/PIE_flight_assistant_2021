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


class Runway(models.Model):
    airport = models.ForeignKey('Airport', on_delete=models.CASCADE)
    length = models.FloatField()
    width = models.FloatField()
    surface = models.CharField(max_length=20)
    le_ident = models.CharField(max_length=5)
    le_heading = models.FloatField()
    le_latitude = models.FloatField()
    le_longitude = models.FloatField()
    le_altitude = models.FloatField()
    he_ident = models.CharField(max_length=5)
    he_heading = models.FloatField()
    he_latitude = models.FloatField()
    he_longitude = models.FloatField()
    he_altitude = models.FloatField()

    def __str__(self):
        return f"(Runway) : {self.le_ident}/{self.he_ident} - {self.airport}"

