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

import json
import logging
import sys

import aiohttp

from virtualtouchpad.dispatchers import Dispatcher, keyboard, mouse

from . import report_error, websocket
from ._util import generate_access_token


def access_control(app, request):
    """Provides access control for the controller by verifying that the
    ``access_token`` parameter is correct.
    """
    access_token = request.url.query.get('access_token')
    if access_token != app['server'].configuration.ACCESS_TOKEN:
        raise aiohttp.web.HTTPForbidden()


@websocket('/controller', access_control)
async def controller(app, request, ws):
    log = logging.getLogger(__name__)
    dispatch = Dispatcher(
        key=keyboard.Handler(),
        mouse=mouse.Handler())

    # Invalidate the access token
    if app['server'].configuration.ACCESS_TOKEN:
        app['server'].configuration.ACCESS_TOKEN = generate_access_token()

    async for message in ws:
        if message.type == aiohttp.WSMsgType.TEXT:
            try:
                dispatch(**json.loads(message.data))
            except Exception as e:
                log.exception(
                    'An error occurred when handling %s',
                    message)
                _, _, tb = sys.exc_info()
                report_error(ws, 'invalid_data', e, tb)

        elif message.type == aiohttp.WSMsgType.ERROR:
            log.error('WebSocket closed with %s', ws.exception())
