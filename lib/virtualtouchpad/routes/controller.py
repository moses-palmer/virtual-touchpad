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
import sys

from virtualtouchpad.dispatchers import Dispatcher, keyboard, mouse

from . import websocket


@websocket('/controller')
def controller(report_error):
    log = logging.getLogger(__name__)
    dispatch = Dispatcher(
        key=keyboard.Handler(),
        mouse=mouse.Handler())

    while True:
        message = yield
        if not message:
            continue

        try:
            command = json.loads(message)
        except Exception as e:
            log.exception(
                'An error occurred when loading JSON from %s',
                message)
            ex_type, ex, tb = sys.exc_info()
            report_error(
                'invalid_data',
                e, tb)
            continue

        try:
            dispatch(**command)
        except TypeError as e:
            log.exception(
                'Failed to dispatch command %s',
                command)
            ex_type, ex, tb = sys.exc_info()
            report_error(
                'invalid_command',
                e, tb)
            continue
