# coding=utf-8
# virtual-touchpad
# Copyright (C) 2013-2015 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.


from .._info import *

from ..platform import *

import gevent

import bottle
import geventwebsocket
import json
import logging
import os
import sys
import traceback

log = logging.getLogger(__name__)

try:
    from geventwebsocket.handler import WebSocketHandler
except ImportError:
    from geventwebsocket import WebSocketHandler

from .dispatch import dispatch

from . import static_file

app = bottle.Bottle()


@app.route('/translations/<domain>')
def translations(domain):
    accept_language = bottle.request.headers.get('Accept-Language') or 'default'
    languages = sorted((
        (
            language.split(';')[0].strip(),
            float(language.split(';q=')[1]) if ';q=' in language else 1.0)
        for language in accept_language.split(',')),
        key = lambda p: p[1],
        reverse = True) + [('default', 0.0)]

    for language, q in languages:
        path = os.path.join('translations', domain, language + '.js')
        if static_file.exists(path):
            return static_file.get(path)

    return bottle.HTTPResponse(status = 404)


@app.route('/ws')
def handle_websocket():
    # Get the actual websocket
    ws = bottle.request.environ.get('wsgi.websocket')
    log.info('WebSocket with %s opened',
        bottle.request.environ.get('REMOTE_ADDR'));
    if not ws:
        bottle.abort(400, 'Expected WebSocket request.')

    def report_error(reason, exception, tb):
        ws.send(json.dumps(dict(
            reason = reason,
            exception = type(exception).__name__,
            data = str(exception),
            tb = traceback.extract_tb(tb))))

    while True:
        try:
            message = ws.receive()
            if message is None:
                break

            try:
                command = json.loads(message)
            except Exception as e:
                log.exception('An error occurred when loading JSON from %s',
                    message)
                ex_type, ex, tb = sys.exc_info()
                report_error('invalid_data',
                    e, tb)
                continue

            try:
                dispatch(command)
            except (KeyError, ValueError, TypeError) as e:
                log.exception('Failed to dispatch command %s',
                    command)
                ex_type, ex, tb = sys.exc_info()
                report_error('invalid_command',
                    e, tb)
                continue
            except Exception as e:
                log.exception('An error occurred while dispatching %s',
                    command)
                ex_type, ex, tb = sys.exc_info()
                report_error('internal_error',
                    e, tb)
                continue

        except geventwebsocket.WebSocketError:
            log.exception('Failed to read WebSocket data')
            break


@app.route('/<filepath:path>')
def static(filepath):
    return static_file.get(filepath)


@app.route('/')
def index():
    return static('index.xhtml')


MINIFIED_XHTML = 'index.min.xhtml'
if static_file.exists(MINIFIED_XHTML):
    @app.route('/')
    def index_minified():
        return static(MINIFIED_XHTML)


def main(port, address, log_level):
    global app

    import gevent.pywsgi
    import geventwebsocket
    import sys

    name, host = address

    sys.stdout.write('Starting server http://%s:%d/...\n' % (
        name, port))

    from gevent import monkey; monkey.patch_all(thread = False)
    return gevent.pywsgi.WSGIServer(
        (host, port),
        app,
        handler_class = WebSocketHandler)
