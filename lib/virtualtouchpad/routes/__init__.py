# coding=utf-8
# virtual-touchpad
# Copyright (C) 2013-2017 Moses Palmér
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
import functools
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
                response = await handler(app, request, **arguments)
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


def report_error(ws, reason, exception=None, tb=None):
    """Sends an error report over a *WebSocket* in a format that is parsable by
    the client.

    :param aiohttp.web.WebSocketResponse ws: The *WebSocket*.

    :param str reason: a computer-parsable reason string.

    :param exception: The exception causing the error.

    :param tb: The traceback.
    """
    ws.send_str(json.dumps(dict(
        reason=reason,
        exception=type(exception).__name__ if exception else None,
        data=str(exception) if exception else None,
        tb=[
            (fs.filename, fs.lineno, fs.name, fs.line)
            for fs in
            traceback.extract_tb(tb)] if tb else None)))


def websocket(path, access_control=lambda app, request: None):
    """A decorator to mark a function as handling incoming *WebSocket* commands.

    This is not a generic *WebSocket* handler; it will only handle incoming
    data.

    The decorated function must be a generator. It will be sent ``None``
    followed by any data received.

    :param str path: The path this function handles.

    :param callable access_control: A callable providing access control. It will
        be called before the request is upgraded, and is passed the parameters
        ``(app, request)``, where ``app`` is the current application, and
        ``request`` is the request to upgrade to a *WebSocket*.
    """
    log = logging.getLogger('%s.%s' % (__name__, path))

    def inner(handler):
        async def wrapper(request):
            access_control(app, request)

            ws = aiohttp.web.WebSocketResponse()
            await ws.prepare(request)

            try:
                await handler(app, request, ws)
            except Exception as e:
                log.exception(
                    'An error occurred in WebSocket handler %s',
                    handler.__name__)

            return ws

        app.router.add_route(
            'GET',
            path,
            wrapper)

        return handler

    return inner


def is_local_request(request):
    """Determines whether a request originates from the local host.

    :param request: The request.

    :return: whether the request originates from the local host
    """
    peername = request.transport.get_extra_info('peername')
    if peername is not None:
        host, _ = peername
        return host == app['server'].configuration.SERVER_HOST
    else:
        return False


def localhost(f):
    """A decorator to restrict access to a route to ``localhost``.

    :param callable f: The route handler.
    """
    @functools.wraps(f)
    def inner(app, request, *args):
        if is_local_request(request):
            return f(app, request, *args)
        else:
            raise aiohttp.web.HTTPForbidden()

    return inner


# Importing these modules will attach routes to app
from . import controller
from . import keyboard
from . import qr
from . import status
from . import translations

# Import files last since it is the catch-all route
from . import files
