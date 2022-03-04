"""
Utils for geographic coordinates
"""
import numpy as np
from math import sin, cos, sqrt, atan2, radians, asin
import math


def coord_to_dist(cur_lat, cur_long, dest_lat, dest_long):
    """ Computes the distance between two coordinates in nm
    """
    cur_lat = cur_lat*np.pi/180
    cur_long = cur_long*np.pi/180
    dest_lat = dest_lat*np.pi/180
    dest_long = dest_long*np.pi/180
    return 60*180/np.pi*np.arccos(np.sin(cur_lat)*np.sin(dest_lat)+np.cos(cur_lat)*np.cos(dest_lat)*np.cos(dest_long-cur_long))


def heading_to_point(lat, lng, point_lat, point_lng):
    # https://www.igismap.com/formula-to-find-bearing-or-heading-angle-between-two-points-latitude-longitude/
    X = cos(point_lat) * sin(point_lng - lng)
    Y = cos(lat)*sin(point_lat) - sin(lat)*cos(point_lat)*cos(point_lng - lng)

    beta = atan2(X, Y) / math.pi * 180
    if beta < 0:
        beta += 360
    return beta



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
        Distance between the point and a flight in km
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

