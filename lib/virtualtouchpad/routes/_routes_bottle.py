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
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import json
import logging
import traceback
import types

import bottle
import geventwebsocket

from virtualtouchpad._server_bottle import app


def get(path):
    """A decorator to mark a function as handling an *HTTP* ``GET`` request.

    Please see :func:`bottle.Application.get` for a reference on the format of
    ``path``.

    The decorated function is passed the request headers, where header names are
    lower case, as its first parameter, and any values extracted from the path.

    :param str path: The path this function handles.
    """
    log = logging.getLogger('%s.%s' % (__name__, path))

    def inner(handler):
        @app.get(path)
        def wrapper(*args, **kwargs):
            try:
                headers = {
                    key.lower(): value
                    for key, value in bottle.request.headers.items()}
                response = handler(headers, *args, **kwargs)
                if isinstance(response, types.DictionaryType):
                    response = HTTPResponse(200, body=json.dumps(response))
                return bottle.HTTPResponse(
                    body=response.body,
                    status=response.status,
                    headers=response.headers)

            except Exception as e:
                log.exception('An error occurred when handling request')
                raise bottle.HTTPError(status=500)

        return handler

    return inner


def websocket(path):
    """A decorator to mark a function as handling incoming *WebSocket* commands.

    This is not a generic *WebSocket* handler; it will only handle incoming
    data.

    The decorated function must be a generator. It will be sent ``None``
    followed by any data received.

    :param str path: The path this function handles.
    """
    log = logging.getLogger('%s.%s' % (__name__, path))

    def inner(handler):
        @app.route(path)
        def wrapper():
            # Get the actual websocket
            ws = bottle.request.environ.get('wsgi.websocket')
            log.info(
                'WebSocket with %s opened',
                bottle.request.environ.get('REMOTE_ADDR'))
            if not ws:
                bottle.abort(400, 'Expected WebSocket request.')

            def report_error(reason, exception, tb):
                ws.send(json.dumps(dict(
                    reason=reason,
                    exception=type(exception).__name__,
                    data=str(exception),
                    tb=traceback.extract_tb(tb))))

            dispatcher = handler(report_error)
            next(dispatcher)

            while True:
                try:
                    message = ws.receive()
                    if message is None:
                        break
                    dispatcher.send(message)

                except geventwebsocket.WebSocketError:
                    log.exception('Failed to read WebSocket data')
                    break

                except Exception as e:
                    log.exception(
                        'An error occurred while dispatching %s',
                        message)
                    break

        return handler

    return inner
