"""
Real-time traffic data handler

"""
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
    """ Computes the distance between a center point and a flight
        based on their GPS coordinates

    Parameters
    ----------
    center_lat : float
        Latitude of the center
    center_lng : float
        Longitude of the center
    flight_lat : float
        Latitude of the flight
    flight_lng : float
        Longitude of the flight

    Returns
    -------
    float
        Distance between the point and a flight
    """
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
    """ Computes a box around a circle with a center and a radius

    Parameters
    ----------
    center : (float, float)
        GPS coordinates of the center
    RADIUS : float
        Radius of the cercle in km

    Returns
    -------
    (float, float, float, float)
        South / North latitude
        West / East longitude
    """
    lat, lng = center
    s, w, n, e = boundingBox(lat, lng, RADIUS)
    return s, n, w, e



class FlightRadar24Handler:
    """
    Traffic handler from FlightRadar24 data
    """
    
    def __init__(self):
        self.api = API()
    
    def get_current_airspace(self, dict_message, center=None, box=None, RADIUS=100, VERBOSE=False):
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

        dict_message['radius'] = RADIUS
        dict_message['time_update_str'] = time_update_str
        dict_message['number_flights'] = number_flights
        dict_message['list_flights'] = list_flights




class AutocompleteQueryHandler():
    def __init__(self):
        self.api = API()
    
    def query_partial_flight(self, query, limit=10):
        list_found = []
        for r in self.api.get_search_results(query=query, limit=limit):
            if r['type'] not in ('schedule', 'aircraft', 'operator', 'airport'):
                route = "?? ⟶ ??" if not r.get('detail').get('route') else r['detail']['route'] 
                str_result = f"{r['detail']['callsign']} : {route}"
                flight_id = r['id']
                # list_found.append(r['detail']['callsign'])
                list_found.append({'str' : str_result, 'id' : flight_id})
        return list_found

    def query_complete_flight(self, flight_id):
        print(flight_id)
        flight = self.api.get_flight(flight_id, RAW=False)
        last_waypoint = flight.trail[0]
        before_waypoint = flight.trail[1]
        dt = last_waypoint.timestamp - before_waypoint.timestamp
        dh = last_waypoint.altitude - before_waypoint.altitude

        return {
            'id': flight.id, 
            'callsign' : flight.flight, 
            'registration' : flight.registration,
            'lat': last_waypoint.latitude, 
            'lon': last_waypoint.latitude,
            'heading': last_waypoint.heading, 
            'speed': last_waypoint.speed, 
            'vertical_speed' : int(60*dh/dt),
            'alt' : last_waypoint.altitude,        
            'last_contact' : last_waypoint.timestamp,
            'origin' : flight.origin, 
            'destination' : flight.destination
        }

