from flask_sqlalchemy import SQLAlchemy
import logging as lg

from .views import app
# Create database connection object
db = SQLAlchemy(app)

class Airport(db.Model):
    name = db.Column(db.String(100), nullable=False)
    iata = db.Column(db.String(3), nullable=False)
    icao = db.Column(db.String(4), nullable=False, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    altitude = db.Column(db.Float, nullable=False)
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



class Runway(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    airport = db.Column(db.String(4), db.ForeignKey('airport.icao'), nullable=False)
    length = db.Column(db.Float, nullable=False)
    width = db.Column(db.Float, nullable=False)
    surface = db.Column(db.String(70), nullable=False)
    le_ident = db.Column(db.String(5), nullable=False)
    le_heading = db.Column(db.Float, nullable=False)
    le_latitude = db.Column(db.Float, nullable=False)
    le_longitude = db.Column(db.Float, nullable=False)
    le_altitude = db.Column(db.Float, nullable=False)
    he_ident = db.Column(db.String(5), nullable=False)
    he_heading = db.Column(db.Float, nullable=False)
    he_latitude = db.Column(db.Float, nullable=False)
    he_longitude = db.Column(db.Float, nullable=False)
    he_altitude = db.Column(db.Float, nullable=False)

    def __init__(self, id, airport, length, width, surface,
                le_ident, le_heading, le_latitude, le_longitude, le_altitude,
                he_ident, he_heading, he_latitude, he_longitude, he_altitude):
        self.id = id
        self.airport = airport
        self.length = length
        self.width = width
        self.surface = surface
        self.le_ident = le_ident
        self.le_heading = le_heading
        self.le_latitude = le_latitude
        self.le_longitude = le_longitude
        self.le_altitude = le_altitude
        self.he_ident = he_ident
        self.he_heading = he_heading
        self.he_latitude = he_latitude
        self.he_longitude = he_longitude
        self.he_altitude = he_altitude

    def __str__(self):
        return f"(Runway) : {self.le_ident}/{self.he_ident} - {self.airport}"
