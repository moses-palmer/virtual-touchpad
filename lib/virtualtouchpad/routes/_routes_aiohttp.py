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

import asyncio
import json
import logging
import re
import traceback

import aiohttp
import aiohttp.web

from virtualtouchpad._server_aiohttp import app


#: The regular expression used to transform bottle variable paths to aiohttp
# variable paths
BOTTLE_RE = re.compile(
    r'<([^:>]+)(?::([^>]+))?>')


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
        @asyncio.coroutine
        def wrapper(request):
            #import pudb; pudb.set_trace()
            arguments = dict(request.match_info)
            try:
                headers = {
                    key.lower(): value
                    for key, value in request.headers.items()}
                response = handler(headers, **arguments)
                if isinstance(response, dict):
                    return aiohttp.web.Response(
                        content_type='application/json',
                        status=200,
                        text=json.dumps(response))
                else:
                    return aiohttp.web.Response(
                        body=response.body,
                        status=response.status,
                        headers=response.headers)

            except Exception as e:
                log.exception('An error occurred when handling request')
                raise aiohttp.web.HTTPInternalServerError()

        def replacer(m):
            try:
                name, extra = m.groups()
                return '{%s:%s}' % (
                    name,
                    dict(
                        path='[^{}]+')[extra])
            except:
                return '{%s}' % m.group(1)
        app.router.add_route(
            'GET',
            BOTTLE_RE.sub(replacer, path),
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
        @asyncio.coroutine
        def wrapper(request):
            ws = aiohttp.web.WebSocketResponse()
            yield from ws.prepare(request)

            def report_error(reason, exception, tb):
                ws.send_str(json.dumps(dict(
                    reason=reason,
                    exception=type(exception).__name__,
                    data=str(exception),
                    tb=traceback.extract_tb(tb))))

            dispatcher = handler(report_error)
            next(dispatcher)

            while True:
                message = yield from ws.receive()
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

        app.router.add_route(
            'GET',
            path,
            wrapper)

        return handler

    return inner
