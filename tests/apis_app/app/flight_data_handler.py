# from flightradar.api import API
# from flightradar.coordinates import *
import time
import requests
import json
import pandas as pd
from datetime import datetime
from .flightradar.api import API
from .flightradar.coordinates import *
try:
    from opensky_api import OpenSkyApi
except ModuleNotFoundError:
    print("OpenSkyAPI package not installed !")


def fprint(*args, **kwargs):
    print(args, flush=True)

class FlightRadar24Handler:

    def __init__(self):
        self.api = API()
    
    def get_current_airspace(self, box):
        # box : (south, north, west, east)
        # area(southwest, northeast)
        # point(lat, lon)
        # need : bounds=45.477,42.628,-1.709,3.683
        s, n, w, e = box
        area = Area(Point(n, w), Point(s, e))
        data_raw = self.api.get_area(area, VERBOSE=False)
        data = json.loads(data_raw)

        list_flights = []
        list_update_times = []

        for k, f in data.items():
            this_flight = {
                'icao24' : f['icao'],
                'callsign' : f['registration'],
                'latitude' : f['lat'],
                'longitude' : f['lon'],
                'heading' : f['track'],
                'altitude' : f['alt'],
            }
            list_flights.append(this_flight)
            list_update_times.append(f['last_contact'])

        ancien_update_time = datetime.utcfromtimestamp(min(list_update_times)).strftime('%H:%M:%S')
        recent_update_time = datetime.utcfromtimestamp(max(list_update_times)).strftime('%H:%M:%S')
        date_update_time = datetime.utcfromtimestamp(min(list_update_times)).strftime('%Y-%m-%d')
        time_update_str = f"{date_update_time} [{ancien_update_time} >> {recent_update_time}]"

        number_flights = len(list_flights)

        dict_message = {
            'time_update_str': time_update_str,
            'number_flights' : number_flights,
            'list_flights' : list_flights
            }
        
        return dict_message







class OpenSkyNetworkHandler:
    username = "" # TO FILL
    password = "" # TO FILL


    def get_current_airspace(self, box):
        api = OpenSkyApi(username=self.username, password=self.password)
        states_box = api.get_states(bbox=box)
        
        time_update_str = datetime.utcfromtimestamp(states_box.time).strftime('%Y-%m-%d %H:%M:%S')
        number_flights = len(states_box.states)
        list_flights = []

        for i, s in enumerate(states_box.states):
            this_flight = {
                'icao24' : s.icao24,
                'callsign' : s.callsign.strip(),
                'latitude' : s.latitude,
                'longitude' : s.longitude,
                'heading' : s.heading,
                'altitude' : s.geo_altitude,
            }
            list_flights.append(this_flight)

        dict_message = {
            'time_update_str': time_update_str,
            'number_flights' : number_flights,
            'list_flights' : list_flights
            }

        return dict_message


    def get_airplane_state(icao24, current_time=None):
        current_time = int(time.time()) if current_time is None else current_time
        session = requests.Session()
        c = session.get(
            f"https://opensky-network.org/api/states/all?time={current_time}&icao24={icao24}"
        )
        c.raise_for_status()
        json_response = c.json()

        df = pd.DataFrame.from_records(
        json_response["states"],
        columns=[
            "icao24",
            "callsign",
            "origin_country",
            "time_position",
            "last_contact",
            "longitude",
            "latitude",
            "baro_altitude",
            "on_ground",
            "velocity",
            "true_track",
            "vertical_rate",
            "sensors",
            "geo_altitude",
            "squawk",
            "spi",
            "position_source",
        ])

        return df