"""
WSGI config for flight_assistant_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import socketio
from django.contrib.staticfiles.handlers import StaticFilesHandler
from app.views import sio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flight_assistant_app.settings')
# django_app = get_wsgi_application()
# application = socketio.WSGIApp(sio, django_app)

django_app = StaticFilesHandler(get_wsgi_application())
application = socketio.Middleware(sio, wsgi_app=django_app, socketio_path='socket.io')




import eventlet
import eventlet.wsgi
eventlet.wsgi.server(eventlet.listen(('', 8000)), application)