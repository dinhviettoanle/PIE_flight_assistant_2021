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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os
from time import sleep
from threading import Thread, Event
import socketio
from random import random
from .flight_data_handler import FlightRadar24Handler, OpenSkyNetworkHandler

import eventlet
eventlet.monkey_patch()

async_mode = 'eventlet' # None ??
sio = socketio.Server(async_mode=async_mode)
airspace_worker = None

def fprint(*args, **kwargs):
    print(args, flush=True)



class AirspaceBackgroundWorker:
    switch = False

    def __init__(self, sio, box):
        self.sio = sio
        self.switch = True
        self.box = (box[1], box[3], box[0], box[2]) # south, north, west, east
        self.flight_data_process = FlightRadar24Handler()
        fprint("----- Background airspace worker initialized -----")

    def do_work(self):
        namespace = '/test'
        fprint("----- Begin trafic worker -----")
        while self.switch:
            dict_message = self.flight_data_process.get_current_airspace(self.box)
            self.sio.emit('airspace', dict_message, namespace=namespace)
            fprint("Flights in the area : ", dict_message['number_flights'])
            eventlet.sleep(1)
    
    def update_box(self, box):
        box_format = (box[1], box[3], box[0], box[2])
        self.box = box_format

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
    global airspace_worker
    box = (-0.04,42.78,2.86,44.62)
    if airspace_worker is not None:
        airspace_worker.update_box(box)
    else:
        airspace_worker = AirspaceBackgroundWorker(sio, box)
        sio.start_background_task(airspace_worker.do_work)



@sio.on('change_focus', namespace='/test')
def get_change_focus(sid, data):
    min_lat, max_lat = data['latitude'] - 1, data['latitude'] + 1
    min_long, max_long = data['longitude'] - 2, data['longitude'] + 2
    box = (min_long, min_lat, max_long, max_lat)
    airspace_worker.update_box(box)

    


@sio.event
def disconnect(sid):
    print('Client disconnected')