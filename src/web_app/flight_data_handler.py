"""
Real-time traffic data handler

"""
import time
import requests
import json
import pandas as pd
from datetime import datetime
from .flightradar.api import API
from .flightradar.coordinates import *
from .geo_utils import *



def fprint(*args, **kwargs):
    print(args, flush=True)



class FlightRadar24Handler:
    """
    Traffic handler from FlightRadar24 data
    """
    
    def __init__(self):
        self.api = API()


    def get_current_airspace(self, dict_message, center=None, box=None, RADIUS=100, VERBOSE=False):
        """ Updates a dictionnary with traffic data within a zone

        Parameters
        ----------
        dict_message : dict
            Dictionnary to update
        center : tuple, optional
            Geo point (lat, lon), by default None
        box : tuple, optional
            Geo box (south, north, west, east), by default None
        RADIUS : int, optional
            Radius of the circle if center is used, by default 100
        VERBOSE : bool, optional
            Displays the url, by default False
        """
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



class AutocompleteHandler():
    """ 
    Handles the auto-completion of the search field
    """
    def __init__(self):
        self.api = API()


    def query_partial_flight(self, query, limit=10):
        """ Gets the result of a query to fr24 API

        Parameters
        ----------
        query : str
            Query to be sent (generally the callsign)
        limit : int, optional
            Number of results, by default 10

        Returns
        -------
        list
            List of dictionaries like
            [{
                'str': string to be displayed in the GUI,
                'id' : unique ID of the flight
            }]
        """
        list_found = []
        for r in self.api.get_search_results(query=query, limit=limit):
            if r['type'] not in ('schedule', 'aircraft', 'operator', 'airport'):
                route = "N/A ⟶ N/A" if not r.get('detail').get('route') else r['detail']['route'] 
                str_result = f"{r['detail']['callsign']} : {route}"
                flight_id = r['id']
                # list_found.append(r['detail']['callsign'])
                list_found.append({'str' : str_result, 'id' : flight_id})
        return list_found




class FlightSpecificQueryHandler():
    def __init__(self):
        self.api = API()

    def get_last_position(self, flight, flight_id):
        detail = self.api.get_search_results(query=flight.flight, limit=1)[0]['detail']
        print(detail['lat'], detail['lon'], flight_id)
        dynamic_data = self.query_dynamic_data(detail['lat'], detail['lon'], flight_id, RADIUS=300)
        print(dynamic_data)
        return Waypoint(
            latitude=dynamic_data['latitude'], 
            longitude=dynamic_data['longitude'], 
            altitude=dynamic_data['altitude'], 
            speed=dynamic_data['speed'], 
            heading=dynamic_data['heading'], 
            timestamp=dynamic_data['last_contact']
        )


    # Attention, risque de "HTTP Error 402: Payment Required" si trop de requetes
    def query_complete_flight(self, flight_id):
        """ Gets the precise flight static data from its ID

        Parameters
        ----------
        flight_id : str
            Flight ID generated by the FR24 API

        Returns
        -------
        dict
            Dictionary containing multiple static stuff
        """
        flight = self.api.get_flight(flight_id, RAW=False, LINK=True)
        # self.api.get_flight(flight_id, RAW=True)
        
        if len(flight.trail) == 0:
            last_waypoint = self.get_last_position(flight, flight_id)
            before_waypoint = last_waypoint
            dt = 1
        elif len(flight.trail) == 1:
            last_waypoint = flight.trail[0]
            before_waypoint = flight.trail[0]
            dt = 1
        else:
            last_waypoint = flight.trail[0]
            before_waypoint = flight.trail[1]
            dt = last_waypoint.timestamp - before_waypoint.timestamp
        
        
        dh = last_waypoint.altitude - before_waypoint.altitude

        return {
            'id': flight.id, 
            'callsign' : flight.flight, 
            'registration' : flight.registration,
            'model' : flight.model,
            'model_text' : flight.model_text,
            'latitude': last_waypoint.latitude, 
            'longitude': last_waypoint.longitude,
            'heading': last_waypoint.heading, 
            'speed': last_waypoint.speed, 
            'vertical_speed' : int(60*dh/dt),
            'altitude' : last_waypoint.altitude,        
            'last_contact' : last_waypoint.timestamp,
            'origin' : flight.origin, 
            'origin_icao' : flight.origin_icao, 
            'destination' : flight.destination,
            'destination_icao' : flight.destination_icao,
            'time_scheduled' : flight.time_scheduled,
            'time_estimated' : flight.time_estimated,
        }


    def query_dynamic_data(self, lat, lng, flight_id, RADIUS=20):
        """ Updates the dynamic data regarding a flight

        Parameters
        ----------
        lat : float
            Current latitude of the flight
        lng : float
            Current longitude of the flight
        flight_id : str
            Flight ID generated by the FR24 API
        RADIUS : int, optional
            Radius of the circle within we search, by default 20

        Returns
        -------
        dict
            Dictionary contianing updated dynamic data regarding a flight
        """""
        center = (lat, lng)
        s, n, w, e = get_box_from_center(center, RADIUS) # Watch 20km around the center

        area = Area(Point(n, w), Point(s, e))
        data_raw = self.api.get_area(area, VERBOSE=False)
        data = json.loads(data_raw)[flight_id]

        return {
            'latitude' : data['lat'],
            'longitude' : data['lon'],
            'heading' : data['track'],
            'speed' : data['speed'],
            'vertical_speed' : data['vertical_speed'],
            'altitude' : data['alt'],
            'last_contact' : datetime.utcfromtimestamp(data['last_contact']).strftime('%H:%M:%S'),
        }



    

