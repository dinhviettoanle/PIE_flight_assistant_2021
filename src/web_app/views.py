"""
Web app views

"""
# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context, request, jsonify
from random import random
from time import sleep
import os
from threading import Thread, Event

from .flight_data_handler import *

import logging
from .query_ontology import *


# =======================================================================
# ===================== FLASK APP INIT ==================================
# =======================================================================
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['DEBUG'] = True


log = logging.getLogger('werkzeug')
log.disabled = True
sio = SocketIO(app, async_mode=None, logger=False, engineio_logger=False)
# ====================================

airspace_worker = None
thread = Thread()
USE_RADAR = True

autocomplete_query_handler = AutocompleteQueryHandler()

# =======================================================================
# ===================== BACKGROUND TASKS ================================
# =======================================================================

def get_near_airports(dict_message, center, RADIUS=100):
    """ Updates the dictionary message sent to the client with airport data

    Parameters
    ----------
    dict_message : dict
        Dictionary sent to the client
    center : (float, float)
        Center of the radar
    RADIUS : float, optional
        Radius of the radar
    """    
    try:
        s, n, w, e = get_box_from_center(center, RADIUS)
        dict_message['list_airports'] = query_map_near_airports(s, n, w, e)
    except Exception as e:
        fprint("Error querying airports", e)
        dict_message['list_airports'] = []


def get_near_runways(dict_message, center, RADIUS=100):
    """ Updates the dictionary message sent to the client with runway data

    Parameters
    ----------
    dict_message : dict
        Dictionary sent to the client
    center : (float, float)
        Center of the radar
    RADIUS : float, optional
        Radius of the radar
    """    
    try:
        s, n, w, e = get_box_from_center(center, RADIUS)
        dict_message['list_runways'] = query_map_near_runways(s, n, w, e)
    except Exception as e:
        fprint("Error querying runways", e)
        dict_message['list_runways'] = []


def get_near_frequencies(dict_message):
    """ Updates the dictionary message sent to the client with frequency data

    Parameters
    ----------
    dict_message : dict
        Dictionary sent to the client
    """    
    event_bug = ""
    for airport in dict_message['list_airports']:
        current_icao = airport['icao']
        try:
            airport['list_frequencies'] = query_map_near_frequencies(current_icao)
        except Exception as e:
            airport['list_frequencies'] = []
            event_bug = e
    
    if event_bug != "":
        fprint("Error querying frequencies", event_bug)


def get_near_navaids(dict_message, center, RADIUS=100):
    """ Updates the dictionary message sent to the client with navaid data

    Parameters
    ----------
    dict_message : dict
        Dictionary sent to the client
    center : (float, float)
        Center of the radar
    RADIUS : float, optional
        Radius of the radar
    """    
    try:
        s, n, w, e = get_box_from_center(center, RADIUS)
        dict_message['list_navaids'] = query_map_near_navaids(s, n, w, e) 
    except Exception as e:
        fprint("Error querying navaids", e)
        dict_message['list_navaids'] = []





class AirspaceBackgroundWorker:
    """
    Thread handling periodic queries and calls to the traffic data API
    """
    switch = False

    def __init__(self, sio, box=None, center=None):
        self.sio = sio
        self.switch = True
        self.box = box
        self.center = center
        self.dict_message = {}
        self.flight_data_process = FlightRadar24Handler()
        self.update_static_data()
        fprint("----- Background airspace worker initialized -----")

    def do_work(self):
        while self.switch:
            try:
                # Handle traffic
                if USE_RADAR:
                    self.flight_data_process.get_current_airspace(self.dict_message, center=self.center)
                else:
                    self.flight_data_process.get_current_airspace(self.dict_message, box=self.box)
        

                self.sio.emit('airspace', self.dict_message)
                fprint(datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 
                    f"# Flights : {self.dict_message['number_flights']}", 
                    f"# Airports : {len(self.dict_message['list_airports'])}",
                    f"# Runways : {len(self.dict_message['list_runways'])}",
                    )
                self.sio.sleep(.5)

            except Exception as e:
                fprint(f"Error : {str(e)}")
    


    def update_static_data(self):
        try:
            self.dict_message['center'] = self.center
            self.dict_message['box'] = self.box

            # Handle airports
            self.dict_message['list_airports'] = []
            get_near_airports(self.dict_message, self.center)

            # # Handle frequencies
            get_near_frequencies(self.dict_message)

            # # Handle runways
            self.dict_message['list_runways'] = []
            get_near_runways(self.dict_message, self.center)
            
            # # Handle navaids
            self.dict_message['list_navaids'] = []
            get_near_navaids(self.dict_message, self.center)
        
        except Exception as e:
                fprint(f"Error : {str(e)}")


    def update_box(self, box):
        self.box = box
        self.update_static_data()

    
    def update_center(self, center):
        self.center = center
        self.update_static_data()

    def stop(self):
        self.switch = False




def start_work(sid):
    global thread, airspace_worker
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


# =======================================================================
# ===================== FLASK APP VIEWS =================================
# =======================================================================

# =============== ROUTE ==========================
@app.route('/')
def index():
    print(request)
    return render_template('index.html')

@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    results = autocomplete_query_handler.query_partial_flight(query=search)
    fprint(f"Follow flight query : {search} , {results}")
    return jsonify(matching_results=results)


# =============== SOCKET =======================
init_ontology_individuals()

@sio.on('init_worker')
def init_worker():
    start_work("start")


@sio.on('change_focus')
def get_change_focus(data):
    fprint(f"Change focus : {data}")
    if USE_RADAR:
        center = (data['latitude'], data['longitude'])
        airspace_worker.update_center(center)
    else:
        min_lat, max_lat = data['latitude'] - 1, data['latitude'] + 1
        min_long, max_long = data['longitude'] - 2, data['longitude'] + 2
        box = (min_lat, max_lat, min_long, max_long)
        airspace_worker.update_box(box)


@sio.on('follow')
def begin_follow_flight(data):
    flight_id = data['flight_id']
    fprint(f"Following flight : {data['label']}")
    flight_data = autocomplete_query_handler.query_complete_flight(flight_id)
    sio.emit('current_flight', flight_data)
    # Update a thread that moves center



@sio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
