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

import bottle
import geventwebsocket
import json
import logging

from . import app
from ..dispatchers import dispatch


log = logging.getLogger(__name__)


@app.route('/controller')
def controller():
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
