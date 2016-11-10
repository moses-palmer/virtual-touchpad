# coding=utf-8
# virtual-touchpad
# Copyright (C) 2013-2016 Moses Palmér
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

import aiohttp
import json
import logging
import traceback

import aiohttp.web

from virtualtouchpad import app


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
        async def wrapper(request):
            arguments = dict(request.match_info)
            try:
                headers = {
                    key.lower(): value
                    for key, value in request.headers.items()}
                response = await handler(app, headers, **arguments)
                if response is None:
                    return aiohttp.web.Response(
                        status=204)
                elif isinstance(response, dict):
                    return aiohttp.web.json_response(response)
                else:
                    return aiohttp.web.Response(
                        body=response.body,
                        status=response.status,
                        headers=response.headers)

            # Let aiohttp handle HTTP exceptions
            except aiohttp.web.HTTPException:
                raise

            except Exception as e:
                log.exception('An error occurred when handling request')
                raise aiohttp.web.HTTPInternalServerError()

        app.router.add_route(
            'GET',
            path,
            wrapper)

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
        async def wrapper(request):
            ws = aiohttp.web.WebSocketResponse()
            await ws.prepare(request)

            def report_error(reason, exception, tb):
                ws.send_str(json.dumps(dict(
                    reason=reason,
                    exception=type(exception).__name__,
                    data=str(exception),
                    tb=traceback.extract_tb(tb))))

            dispatcher = handler(report_error)
            next(dispatcher)

            while True:
                message = await ws.receive()
                if message.tp == aiohttp.MsgType.text:
                    try:
                        dispatcher.send(message.data)
                    except Exception as e:
                        log.exception(
                            'An error occurred while dispatching %s',
                            message)
                        break
                else:
                    break

            return ws

        app.router.add_route(
            'GET',
            path,
            wrapper)

        return handler

    return inner


# Importing these modules will attach routes to app
from . import controller
from . import keyboard
from . import status
from . import translations

# Import files last since it is the catch-all route
from . import files
