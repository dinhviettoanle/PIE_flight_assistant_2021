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


async_mode = None
sio = socketio.Server(async_mode=async_mode)
thread = Thread()

def fprint(*args, **kwargs):
    print(args, flush=True)




def app(request):
    global thread
    print("Client connected")
    if not thread.isAlive():
        thread = sio.start_background_task(get_proxim_flights_open_sky)
    return render(request, 'index.html', locals())


def redirect_app(request):
    return redirect('app')




def get_proxim_flights_open_sky():
    namespace = '/test'
    # flight_data_process = OpenSkyNetworkHandler()
    flight_data_process = FlightRadar24Handler()
    while True:
        box = (-0.04,42.78,2.86,44.62)
        box = (box[1], box[3], box[0], box[2]) # south, north, west, east
        dict_message = flight_data_process.get_current_airspace(box)
        sio.emit('airspace', dict_message, namespace=namespace)
        sio.sleep(1)


@sio.on('change_focus', namespace='/test')
def get_change_focus(sid, data):
    new_latitude = data['latitude']
    new_longitude = data['longitude']
    fprint(new_latitude, new_longitude)


@sio.event
def disconnect(sid):
    print('Client disconnected')