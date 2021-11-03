# from flightradar.api import API
# from flightradar.coordinates import *
import time
import requests
import json
import pandas as pd
from datetime import datetime
from math import sin, cos, sqrt, atan2, radians, asin
import math
from .flightradar.api import API
from .flightradar.coordinates import *

def fprint(*args, **kwargs):
    print(args, flush=True)

def dist_flight_center(center_lat, center_lng, flight_lat, flight_lng):
    R = 6373.0

    lat1, lon1 = radians(center_lat), radians(center_lng)
    lat2, lon2 = radians(flight_lat), radians(flight_lng)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

# From https://stackoverflow.com/questions/238260/how-to-calculate-the-bounding-box-for-a-given-lat-lng-location
# degrees to radians
def deg2rad(degrees):
    return math.pi*degrees/180.0
# radians to degrees
def rad2deg(radians):
    return 180.0*radians/math.pi

# Semi-axes of WGS-84 geoidal reference
WGS84_a = 6378137.0  # Major semiaxis [m]
WGS84_b = 6356752.3  # Minor semiaxis [m]

# Earth radius at a given latitude, according to the WGS-84 ellipsoid [m]
def WGS84EarthRadius(lat):
    # http://en.wikipedia.org/wiki/Earth_radius
    An = WGS84_a*WGS84_a * math.cos(lat)
    Bn = WGS84_b*WGS84_b * math.sin(lat)
    Ad = WGS84_a * math.cos(lat)
    Bd = WGS84_b * math.sin(lat)
    return math.sqrt( (An*An + Bn*Bn)/(Ad*Ad + Bd*Bd) )

# Bounding box surrounding the point at given coordinates,
# assuming local approximation of Earth surface as a sphere
# of radius given by WGS84
def boundingBox(latitudeInDegrees, longitudeInDegrees, halfSideInKm):
    lat = deg2rad(latitudeInDegrees)
    lon = deg2rad(longitudeInDegrees)
    halfSide = 1000*halfSideInKm

    # Radius of Earth at given latitude
    radius = WGS84EarthRadius(lat)
    # Radius of the parallel at given latitude
    pradius = radius*math.cos(lat)

    latMin = lat - halfSide/radius
    latMax = lat + halfSide/radius
    lonMin = lon - halfSide/pradius
    lonMax = lon + halfSide/pradius

    return (rad2deg(latMin), rad2deg(lonMin), rad2deg(latMax), rad2deg(lonMax))


def get_box_from_center(center, RADIUS):
    lat, lng = center
    s, w, n, e = boundingBox(lat, lng, RADIUS)
    return s, n, w, e



class FlightRadar24Handler:

    def __init__(self):
        self.api = API()
    
    def get_current_airspace(self, center=None, box=None, RADIUS=100, VERBOSE=False):
        # box : (south, north, west, east)
        # area(southwest, northeast)
        # point(lat, lon)
        # need : bounds=45.477,42.628,-1.709,3.683

        if center and not(box):
            lat, lng = center
            s, n, w, e = get_box_from_center(center, RADIUS)
        elif box and not(center):
            s, n, w, e = box
        else:
            raise AttributeError("Specify a center or a box")

        if VERBOSE:
            fprint(f"Box : {n, s, e, w} ; Center : {center}")        
        
        area = Area(Point(n, w), Point(s, e))
        data_raw = self.api.get_area(area, VERBOSE=VERBOSE)
        data = json.loads(data_raw)

        list_flights = []
        list_update_times = []

        for k, f in data.items():
            add_flight = True
            
            if center:
                dist = dist_flight_center(lat, lng, f['lat'], f['lon'])
                add_flight = dist < RADIUS
            
            if add_flight:
                this_flight = {
                    'icao24' : f['icao'],
                    'callsign' : f['registration'],
                    'latitude' : f['lat'],
                    'longitude' : f['lon'],
                    'heading' : f['track'],
                    'altitude' : f['alt'],
                    'speed' : f['speed'],
                    'vertical_speed' : f['vertical_speed'],
                    'origin' : f['origin'],
                    'destination' : f['destination'],
                }        
                list_flights.append(this_flight)
                list_update_times.append(f['last_contact'])

         
        number_flights = len(list_flights)
        
        if number_flights > 0:
            ancien_update_time = datetime.utcfromtimestamp(min(list_update_times)).strftime('%H:%M:%S')
            recent_update_time = datetime.utcfromtimestamp(max(list_update_times)).strftime('%H:%M:%S')
            date_update_time = datetime.utcfromtimestamp(min(list_update_times)).strftime('%Y-%m-%d')
            time_update_str = f"{date_update_time} [{ancien_update_time} >> {recent_update_time}]"
        else:
            time_update_str = "No flight"

        dict_message = {
            'time_update_str': time_update_str,
            'number_flights' : number_flights,
            'list_flights' : list_flights,
            'center' : center,
            'radius' : RADIUS,
            'box' : box,
            }
        
        return dict_message







