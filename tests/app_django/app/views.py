from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.dateformat import format
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.db import models
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
import os
from datetime import datetime
from time import sleep
import json
from threading import Thread, Event
import socketio
from random import random
from .flight_data_handler import FlightRadar24Handler, OpenSkyNetworkHandler, get_box_from_center
from .models import Airport

# import eventlet
# eventlet.monkey_patch()

async_mode = None # None ??
sio = socketio.Server(async_mode=async_mode)
airspace_worker = None
thread = Thread()
USE_RADAR = True

class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, YourCustomType):
            return str(obj)
        return super().default(obj)


def fprint(*args, **kwargs):
    print(args, flush=True)

def get_near_airports(dict_message, center, RADIUS=100):
    s, n, w, e = get_box_from_center(center, RADIUS)
    near_airports = Airport.objects.filter(
        Q(longitude__gte = w) & Q(longitude__lte = e) &
        Q(latitude__gte = s) & Q(latitude__lte = n)
    ).values('name', 'iata', 'icao', 'latitude', 'longitude', 'altitude', 'country', 'desc')
    dict_message['list_airports'] = list(near_airports)




class AirspaceBackgroundWorker:
    switch = False

    def __init__(self, sio, box=None, center=None):
        self.sio = sio
        self.switch = True
        self.box = box
        self.center = center
        self.flight_data_process = FlightRadar24Handler()
        fprint("----- Background airspace worker initialized -----")

    def do_work(self):
        namespace = '/test'
        fprint("----- Begin trafic worker -----")
        while self.switch:
            try:
                # Handle traffic
                if USE_RADAR:
                    dict_message = self.flight_data_process.get_current_airspace(center=self.center)
                else:
                    dict_message = self.flight_data_process.get_current_airspace(box=self.box)
            
                # Handle airports
                get_near_airports(dict_message, self.center)
                
                self.sio.emit('airspace', dict_message, namespace=namespace)
                fprint(datetime.now().strftime("%d-%m-%Y %H:%M:%S"), f"# Flights : {dict_message['number_flights']}", f"# Airports : {len(dict_message['list_airports'])}")
                self.sio.sleep(1)

            except Exception as e:
                fprint(f"Error : {str(e)}")
    
    
    def update_box(self, box):
        self.box = box
    
    def update_center(self, center):
        self.center = center

    def stop(self):
        self.switch = False


def app(request):
    print("Client connected")
    start_work("start")
    return render(request, 'index.html', locals())


def redirect_app(request):
    return redirect('app')


# @sio.on('start', namespace='/test')
def start_work(sid):
    global thread, airspace_worker
    toulouse_lat, toulouse_long = 43.59972466458162, 1.4492797572165728
    min_lat, max_lat = toulouse_lat - 1, toulouse_lat + 1
    min_long, max_long = toulouse_long - 2, toulouse_long + 2
    box = (min_lat, max_lat, min_long, max_long)
    center = (toulouse_lat, toulouse_long)

    if not thread.isAlive():
        if airspace_worker is not None:
            if USE_RADAR: airspace_worker.update_center(center)
            else: airspace_worker.update_box(box)
        else:
            airspace_worker = AirspaceBackgroundWorker(sio, box=box, center=center)
            sio.start_background_task(airspace_worker.do_work)
        



@sio.on('change_focus', namespace='/test')
def get_change_focus(sid, data):
    fprint(f"Change focus : {data}")
    if USE_RADAR:
        center = (data['latitude'], data['longitude'])
        airspace_worker.update_center(center)
    else:
        min_lat, max_lat = data['latitude'] - 1, data['latitude'] + 1
        min_long, max_long = data['longitude'] - 2, data['longitude'] + 2
        box = (min_lat, max_lat, min_long, max_long)
        airspace_worker.update_box(box)

    


@sio.event
def disconnect(sid):
    print('Client disconnected')