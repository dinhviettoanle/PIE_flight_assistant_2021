"""
Web app views

"""
# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context, request, jsonify
from random import random
import os
from threading import Thread, Event

from .flight_data_handler import *

import logging
import traceback
from .log_utils import *
from .query_ontology import *
from .nlu import *


# =======================================================================
# ===================== FLASK APP INIT ==================================
# =======================================================================
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['DEBUG'] = True


log = logging.getLogger('werkzeug')
log.disabled = True
sio = SocketIO(app, async_mode=None, logger=False, engineio_logger=False, cors_allowed_origins="*")
# ====================================

airspace_worker = None
flight_follower_worker = None
thread = Thread()
USE_RADAR = True
SLEEP_TIME = .5
ontology_is_init = False

autocomplete_handler = AutocompleteHandler()



# =======================================================================
# ===================== BACKGROUND TASKS ================================
# =======================================================================

def get_near_airports(surrounding_data, center, RADIUS=100):
    """ Updates the dictionary message sent to the client with airport data

    Parameters
    ----------
    surrounding_data : dict
        Dictionary sent to the client containing all the data
    center : (float, float)
        Center of the radar
    RADIUS : float, optional
        Radius of the radar
    """    
    try:
        s, n, w, e = get_box_from_center(center, RADIUS)
        surrounding_data['list_airports'] = query_map_near_airports(s, n, w, e)
    except Exception as e:
        print_error("Error querying airports", e)
        surrounding_data['list_airports'] = []


def get_near_runways(surrounding_data, center, RADIUS=100):
    """ Updates the dictionary message sent to the client with runway data

    Parameters
    ----------
    surrounding_data : dict
        Dictionary sent to the client containing all the data
    center : (float, float)
        Center of the radar
    RADIUS : float, optional
        Radius of the radar
    """    
    try:
        s, n, w, e = get_box_from_center(center, RADIUS)
        surrounding_data['list_runways'] = query_map_near_runways(s, n, w, e)
    except Exception as e:
        print_error("Error querying runways", e)
        surrounding_data['list_runways'] = []


def get_near_frequencies(surrounding_data):
    """ Updates the dictionary message sent to the client with frequency data

    Parameters
    ----------
    surrounding_data : dict
        Dictionary sent to the client containing all the data
    """    
    event_bug = ""
    for airport in surrounding_data['list_airports']:
        current_icao = airport['icao']
        try:
            airport['list_frequencies'] = query_map_near_frequencies(current_icao)
        except Exception as e:
            airport['list_frequencies'] = []
            event_bug = e
    
    if event_bug != "":
        print_error("Error querying frequencies", event_bug)


def get_near_navaids(surrounding_data, center, RADIUS=100):
    """ Updates the dictionary message sent to the client with navaid data

    Parameters
    ----------
    surrounding_data : dict
        Dictionary sent to the client containing all the data
    center : (float, float)
        Center of the radar
    RADIUS : float, optional
        Radius of the radar
    """    
    try:
        s, n, w, e = get_box_from_center(center, RADIUS)
        surrounding_data['list_navaids'] = query_map_near_navaids(s, n, w, e) 
    except Exception as e:
        print_error("Error querying navaids", e)
        surrounding_data['list_navaids'] = []


def get_near_waypoints(surrounding_data, center, RADIUS=100):
    """ Updates the dictionary message sent to the client with waypoint data

    Parameters
    ----------
    surrounding_data : dict
        Dictionary sent to the client containing all the data
    center : (float, float)
        Center of the radar
    RADIUS : float, optional
        Radius of the radar
    """    
    try:
        s, n, w, e = get_box_from_center(center, RADIUS)
        surrounding_data['list_waypoints'] = query_map_near_waypoints(s, n, w, e)
    except Exception as e:
        print_error("Error querying navaids", e)
        surrounding_data['list_waypoints'] = []





class AirspaceBackgroundWorker:
    """
    Thread handling periodic queries and calls to the traffic data API and to the static data
    """
    switch = False

    def __init__(self, sio, box=None, center=None):
        self.sio = sio
        self.switch = True
        self.box = box
        self.center = center
        self.surrounding_data = {}
        self.flight_data_process = FlightRadar24Handler()
        self.update_static_data()

        print_info("----- Background airspace worker initialized -----")


    def do_work(self):
        """ Main loop of the airspace thread
        """
        while self.switch:
            try:
                # Handle traffic
                if USE_RADAR:
                    self.flight_data_process.get_current_airspace(self.surrounding_data, center=self.center)
                else:
                    self.flight_data_process.get_current_airspace(self.surrounding_data, box=self.box)
        

                self.sio.emit('airspace', self.surrounding_data)

                print_info(datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 
                    f"# Flights : {self.surrounding_data['number_flights']}", 
                    f"# Airports : {len(self.surrounding_data['list_airports'])}",
                    f"# Runways : {len(self.surrounding_data['list_runways'])}",
                    )

                self.sio.sleep(SLEEP_TIME)

            except Exception as e:
                print_error(f"Error : {str(e)}")
    

    def update_static_data(self):
        """ Updates static data (airport, runways, navaids, waypoints), when focus changes
        """
        try:
            self.surrounding_data['center'] = self.center
            self.surrounding_data['box'] = self.box

            # Handle airports
            self.surrounding_data['list_airports'] = []
            get_near_airports(self.surrounding_data, self.center)

            # # Handle frequencies
            get_near_frequencies(self.surrounding_data)

            # # Handle runways
            self.surrounding_data['list_runways'] = []
            get_near_runways(self.surrounding_data, self.center)
            
            # # Handle navaids
            self.surrounding_data['list_navaids'] = []
            get_near_navaids(self.surrounding_data, self.center)

            # # Handle waypoints
            self.surrounding_data['list_waypoints'] = []
            get_near_waypoints(self.surrounding_data, self.center)
        
        except Exception as e:
                print_error(f"Error airspace : {str(e)}")


    def update_box(self, box):
        """ Updates the focus box

        Parameters
        ----------
        box : tuple
            New box
        """
        self.box = box
        self.update_static_data()

    
    def update_center(self, center):
        """ Updates the focus center

        Parameters
        ----------
        center : tuple
            New center
        """
        self.center = center
        self.update_static_data()


    def stop(self):
        self.switch = False





class FlightFollowerWorker:
    """ 
    Thread handling the follow-up of a specific flight
    """
    def __init__(self, sio, airspace_worker):
        self.sio = sio
        self.flight_id = ""
        self.switch = True
        self.is_following = False
        self.flight_follower_query = FlightSpecificQueryHandler()

        # To search near this position
        self.latitude = 0
        self.longitude = 0
        self.static_info = {
            'id' : "",
            'registration' : "",
            'callsign' : "",
            'model' : "",
            'model_text' : "",
            'origin' : "",
            'origin_icao' : "",
            'destination' : "",
            'destination_icao' : ""
        }

        self.airspace_worker = airspace_worker


    def do_work(self):
        """ Main loop of the follow-up worker
        """
        while self.switch:
            try:
                if self.is_following:
                    dynamic_data =  self.flight_follower_query.query_dynamic_data(self.latitude, self.longitude, self.flight_id)
                    # Move box around the current followed flight
                    self.latitude = dynamic_data['lat']
                    self.longitude = dynamic_data['lon']

                    flight_data = self.static_info.copy()
                    for k in dynamic_data:
                        flight_data[k] = dynamic_data[k]

                    print_info(datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                        f"Following {self.flight_id}")
                else:
                    flight_data = {}
                    print_info(datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                        f"Not following")

                flight_data['is_following'] = self.is_following
                
                self.sio.emit('follow_flight_info', flight_data)
                self.sio.sleep(SLEEP_TIME)

            except Exception as e:
                # print_error(traceback.format_exc())
                print_error(f"Error following flight : {type(e).__name__} {str(e)}")


    def update_flight_static_info(self, flight_id):
        """ Gets the static data of the flight (callsign, departure, arrival, ...)

        Parameters
        ----------
        flight_id : str
            Flight ID
        """
        self.is_following = True
        self.flight_id = flight_id
        current_flight_data =  self.flight_follower_query.query_complete_flight(self.flight_id)
        self.latitude = current_flight_data['lat']
        self.longitude = current_flight_data['lon']

        for k in self.static_info:
            self.static_info[k] = current_flight_data[k]


    def stop_following(self):
        self.is_following = False
        self.flight_id = ''


    @timeit
    def handle_query(self, query_type):
        """ Gets the response to a query

        Parameters
        ----------
        query_type : str
            ID of the Query
        """
        response_str = "N/A"
        args = None

        if "?" in query_type:
            query_type, arg = query_type.split("?")
            print_event(f"Query for {query_type}. Argument : {arg}")
        else:
            print_event(f"Query for {query_type}")

        if query_type == "departureAirport":
            response_str = f"The departure airport is {self.static_info.get('origin')}."
        
        elif query_type == "nearestAirport":
            response_dict = query_nearest_airport(self.latitude, self.longitude)
            response_str = f"The nearest airport is {response_dict.get('name')} ({response_dict.get('ICAO')}) at {response_dict.get('distance'):.2f} nm."

        elif query_type == "runwaysAtArrival":
            response_dict = query_runways_at_arrival(self.static_info.get('destination_icao'))
            if response_dict.get('status'):
                list_runways_arrival = response_dict.get('list_runways')
                response_str = f"""Runways at {self.static_info.get('destination')} ({response_dict.get('icao')}) are {", ".join(list_runways_arrival[:-1])} and {list_runways_arrival[-1]}."""
            else:
                response_str = f"Arrival airport is not available."

        elif query_type == "temperatureAtArrival":
            response_dict = query_temperature_at_airport(self.static_info.get('destination_icao'))
            if response_dict.get('status'):
                list_runways_arrival = response_dict.get('list_runways')
                response_str = f"The temperature at {response_dict.get('airport_name')} is {response_dict.get('temperature')} celsius."
            else:
                response_str = f"Arrival airport is not available."

        elif query_type == "windAtAirport":
            response_dict = query_wind_at_airport(arg)
            if response_dict.get('status'):
                response_str = f"The wind at {response_dict.get('airport_name')} is {response_dict.get('wind_orientation')}° {response_dict.get('wind_speed')} kt."
            else:
                response_str = f"This airport is not available."

        elif query_type == "checklistLanding":
            response_dict = get_checklist('landing', self.static_info.get('model'))
            response_str = "CHECKLIST"
            args = {
                'name' : 'Landing checklist',
                'checklist' : response_dict.get('checklist')
            }

        elif query_type == "checklistApproach":
            response_dict = get_checklist('approach', self.static_info.get('model'))
            response_str = "CHECKLIST"
            args = {
                'name' : 'Approach checklist',
                'checklist' : response_dict.get('checklist')
            }

        elif query_type == "clear":
            response_str = "&nbsp;"

        
        return {'response_str' : response_str, 'args': args}




def start_work(sid):
    """ Starts all the background workers (airspace, follow-up)

    Parameters
    ----------
    sid : str
        Action to do
    """
    global thread, airspace_worker, flight_follower_worker
    toulouse_lat, toulouse_long = 43.59972466458162, 1.4492797572165728
    min_lat, max_lat = toulouse_lat - 1, toulouse_lat + 1
    min_long, max_long = toulouse_long - 2, toulouse_long + 2
    box = (min_lat, max_lat, min_long, max_long)
    center = (toulouse_lat, toulouse_long)

    if not thread.is_alive():
        if airspace_worker is not None:
            if USE_RADAR: airspace_worker.update_center(center)
            else: airspace_worker.update_box(box)
        else:
            airspace_worker = AirspaceBackgroundWorker(sio, box=box, center=center)
            sio.start_background_task(airspace_worker.do_work)

        if flight_follower_worker is not None:
            flight_follower_worker.stop_following()
        else:
            flight_follower_worker = FlightFollowerWorker(sio, airspace_worker)
            sio.start_background_task(flight_follower_worker.do_work)




# =======================================================================
# ===================== FLASK APP VIEWS =================================
# =======================================================================

# =============== ROUTE ==========================
@app.route('/')
def index():
    print_event(request)
    return render_template('index.html')

@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    results = autocomplete_handler.query_partial_flight(query=search)
    return jsonify(matching_results=results)


# Query by button
@app.route('/_query', methods=['GET'])
def receive_query():
    query_type = request.args.get('q').split('-')[1]
    
    if request.args.get('arg1'):
        query_type += f"?{request.args.get('arg1')}"
    if request.args.get('arg2'):
        query_type += f"?{request.args.get('arg2')}"

    response_str = flight_follower_worker.handle_query(query_type)
    return jsonify(response=response_str)

# Query by speech recognition
@app.route('/_transcript', methods=['GET'])
def get_speech_transcript():
    transcript = request.args.get('transcript')
    query_type = process_transcript(transcript)
    response_str = flight_follower_worker.handle_query(query_type)
    return jsonify({"success" : True, "response" : response_str})


# =============== SOCKET =======================
init_ontology_individuals()
init_dataframes_individuals()
load_nlu_engine()

@sio.on('init_worker')
def init_worker():
    start_work("start")


@sio.on('change_focus')
def get_change_focus(data):
    print_event(f"Change focus : {data}")
    if USE_RADAR:
        center = (data['latitude'], data['longitude'])
        airspace_worker.update_center(center)
    else:
        min_lat, max_lat = data['latitude'] - 1, data['latitude'] + 1
        min_long, max_long = data['longitude'] - 2, data['longitude'] + 2
        box = (min_lat, max_lat, min_long, max_long)
        airspace_worker.update_box(box)

    if not(data['follow']):
        flight_follower_worker.stop_following()


@sio.on('new_follow')
def new_follow_flight(data):
    flight_id = data['flight_id']
    print_event(f"New follow flight : {data['label']}")
    # Update a thread that moves center
    flight_follower_worker.update_flight_static_info(flight_id)





@sio.on('disconnect')
def test_disconnect():
    print_event('Client disconnected')
