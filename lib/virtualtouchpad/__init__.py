# coding=utf-8
'''
virtual-touchpad
Copyright (C) 2013 Moses Palmér

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
'''

import gevent
from gevent import monkey; monkey.patch_all()

import bottle
import geventwebsocket
import json
import os

try:
    from geventwebsocket.handler import WebSocketHandler
except ImportError:
    from geventwebsocket import WebSocketHandler

from .dispatch import dispatch

app = bottle.Bottle()

STATIC_ROOT = os.getenv('VIRTUAL_TOUCHPAD_STATIC_ROOT')


@app.route('/ws')
def handle_websocket():
    # Get the actual websocket
    ws = bottle.request.environ.get('wsgi.websocket')
    if not ws:
        bottle.abort(400, 'Expected WebSocket request.')

    while True:
        try:
            message = ws.receive()
            try:
                command = json.loads(message)
                dispatch(command)

            except (KeyError, ValueError, TypeError):
                bottle.abort(400, 'Invalid command')

        except geventwebsocket.WebSocketError:
            break


@app.route('/<filepath:path>')
def static(filepath):
    global STATIC_ROOT
    return bottle.static_file(filepath, root = STATIC_ROOT)


@app.route('/')
def index():
    return static('index.html')


def main(port = 16080):
    global app

    import gevent.pywsgi
    import geventwebsocket

    host = "0.0.0.0"

    server = gevent.pywsgi.WSGIServer(
        (host, port),
        app,
        handler_class = WebSocketHandler)
    server.serve_forever()
