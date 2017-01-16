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

import asyncio
import functools
import json
import logging

from . import get, is_local_request, websocket


@get('/status')
async def status(app, request):
    local = is_local_request(request)
    return {
        v.name: value
        for (v, value) in app['server'].configuration.values
        if local or not v.private}


@websocket('/status/updates')
async def status_updates(app, request, ws):
    log = logging.getLogger(__name__)

    def on_notified(item, value):
        ws.send_str(json.dumps({
            'item': item,
            'value': value}))

    with app['server'].configuration.notifier.registered(
            functools.partial(app.loop.call_soon, on_notified)):
        async for message in ws:
            log.info('Received status message: %s', message.data)
