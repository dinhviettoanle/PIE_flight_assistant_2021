from flask_sqlalchemy import SQLAlchemy
import logging as lg

from .views import app
# Create database connection object
db = SQLAlchemy(app)

class Airport(db.Model):
    name = db.Column(db.String(100), nullable=False)
    iata = db.Column(db.String(3), nullable=False)
    icao = db.Column(db.String(4), nullable=False, primary_key=True)
    latitude = db.Column(db.Float, primary_key=True)
    longitude = db.Column(db.Float, primary_key=True)
    altitude = db.Column(db.Float, primary_key=True)
    country = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(50), nullable=True)
    municipality = db.Column(db.String(100), nullable=True)


    def __init__(self, name, iata, icao, 
                latitude, longitude, altitude, 
                country, desc, municipality):
        self.name = name
        self.iata = iata
        self.icao = icao
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.country = country
        self.desc = desc
        self.municipality = municipality
    
    def __str__(self):
        return f"(Airport) : {self.icao}"





