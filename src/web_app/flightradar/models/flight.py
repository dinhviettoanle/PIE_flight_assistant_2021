import json
from typing import List

from ..coordinates import Waypoint

# Example : ["3986ED", 44.4919, -0.0311, 7, 26425, 410,
#           "1000", "F-LFBO1", "E170", "F-HBXN", 1633869495, 
#           "PUF", "CDG", "AF7535", 0, 
#           1344, "AFR93XT", 0, "AFR"]

FIELDS = ['mode_s', 'lat', 'lon', 'track', 'alt', 'speed',
          'squawk', 'radar', 'model', 'registration', 'last_contact',
          'origin', 'destination', 'iata', 'undefined2',
          'vertical_speed', 'icao', 'undefined3', 'airline']
FLIGHT_STRING = ('Flight {flight} from {origin} to {destination}. '
                 '{model} ({registration}) at {lat}, {lon} on altitude {alt}. '
                 'Speed: {speed}. Track: {track}.')
TRACKS = {0: '1', 15: '2', 30: '3', 45: '4', 60: '5', 75: '6', 90: '7',
          105: '8', 120: '9', 135: '10', 150: '11', 165: '12', 180: '13',
          195: '14', 210: '15', 225: '16', 240: '17', 255: '18', 270: '19',
          285: '20', 300: '21', 315: '22', 330: '23', 345: '24', 360: '25'}


class BriefFlight:
    """Class for storing info for all flights on the map."""
    def __init__(self, flight_id, lat, lon, model, registration, origin,
                 destination, iata, icao, airline, mode_s=None, track=None,
                 alt=None, speed=None, squawk=None, radar=None,
                 vertical_speed=None, last_contact=None, undefined2=None,
                 undefined3=None):
        self.id = flight_id
        self.mode_s = mode_s
        self.lat = lat
        self.lon = lon
        self.track = track
        self.alt = alt
        self.speed = speed
        self.squawk = squawk
        self.radar = radar
        self.model = model
        self.registration = registration
        self.last_contact = last_contact
        self.origin = origin
        self.destination = destination
        self.iata = iata
        self.undefined2 = undefined2
        self.vertical_speed = vertical_speed
        self.icao = icao
        self.undefined3 = undefined3
        self.airline = airline

    def __str__(self) -> str:
        return FLIGHT_STRING.format(flight=self.icao,
                                    origin=self.origin,
                                    destination=self.destination,
                                    model=self.model,
                                    registration=self.registration,
                                    lat=self.lat, lon=self.lon,
                                    alt=self.alt, speed=self.speed,
                                    track=self.track)

    @staticmethod
    def create(flight_id: str, data: list):
        """Static method for Flight instance creation."""
        return BriefFlight(flight_id=flight_id, **dict(zip(FIELDS, data)))

    @staticmethod
    def create_from_search(detail: dict, **kwargs):
        """Static method for Flight instance creation from search results."""
        if not(detail.get('flight')) : detail['flight'] = ""
        return BriefFlight(flight_id=kwargs['res_id'], lat=detail['lat'],
                           lon=detail['lon'],
                           origin=detail['route'],
                           destination=detail['route'],
                           model=detail['ac_type'], registration=detail['reg'],
                           icao=detail['callsign'], iata=detail['flight'],
                           airline=detail['operator'])


class DetailedFlight:
    """Class for storing info of selected flight.
    Must be displayed separately."""
    def __init__(self, flight_id, flight, status, model, registration, airline,
                 origin, destination, trail, iata, icao, origin_icao, destination_icao):
        self.id = flight_id
        self.flight = flight
        self.status = status
        self.model = model
        self.registration = registration
        self.airline = airline
        self.icao = icao
        self.iata = iata
        self.origin = origin
        self.origin_icao = origin_icao
        self.destination = destination
        self.destination_icao = destination_icao
        self.trail = self.collect_trail(trail)

    @staticmethod
    def collect_trail(waypoints: list) -> List[Waypoint]:
        """Converts JSON list of points into list of Waypoint instances."""
        return [Waypoint(point['lat'],
                         point['lng'],
                         point['alt'],
                         point['spd'],
                         point['hd'],
                         point['ts']) for point in waypoints]



    @staticmethod
    def create(data: dict):
        """Static method for Flight instance creation."""
        
        try: this_model = data['aircraft']['model']['code']
        except KeyError: this_model = 'N/A'

        try: this_registration = data['aircraft']['registration']
        except KeyError: this_registration = 'N/A'



        return DetailedFlight(
            flight_id=data['identification']['id'],
            flight=data['identification']['callsign'],
            status=data['status']['text'],
            model=this_model,
            registration=this_registration,
            airline=data['airline']['name'] if data['airline'] else 'N/A',
            iata=get_airline_prop(data, 'iata'),
            icao=get_airline_prop(data, 'icao'),
            origin=data['airport']['origin']['name'] if data['airport']['origin'] else 'N/A',
            origin_icao=data['airport']['origin']['code']['icao'] if data['airport']['origin'] else 'N/A',
            destination=data['airport']['destination']['name'] if data['airport']['destination'] else 'N/A',
            destination_icao=data['airport']['destination']['code']['icao'] if data['airport']['destination'] else 'N/A',
            trail=data['trail']
        )

    def __str__(self) -> str:
        return 'Flight {} from {} to {}, {} ({}).'.format(
            self.flight,
            self.origin,
            self.destination,
            self.model,
            self.registration)


def flights_to_json(flights: List[BriefFlight]):
    data = {}
    for flight in flights:
        data[flight.id] = {'id': flight.id, 'icao' : flight.icao, 'registration' : flight.registration,
                           'mode_s' : flight.mode_s,
                           'lat': flight.lat, 'lon': flight.lon,
                           'track': flight.track, 'speed': flight.speed, 'vertical_speed' : flight.vertical_speed,
                           'alt' : flight.alt,
                           'last_contact' : flight.last_contact,
                           'origin' : flight.origin, 'destination' : flight.destination
                           }
    return json.dumps(data)


def get_image_id(track: int) -> int:
    return TRACKS[min(TRACKS, key=lambda x: abs(x - track))]

def get_airline_prop(data, prop):
    try:
        return data['airline']['code'][prop]
    except:
        return 'N/A'