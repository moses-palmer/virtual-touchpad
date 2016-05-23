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

import sys

if sys.version_info.major < 3:
    from ._routes_bottle import get, websocket
else:
    from ._routes_aiohttp import get, websocket


class HTTPResponse(object):
    """A lightweight class to represent an HTTP response.
    """
    def __init__(self, status, body=None, headers=None):
        self.status = status
        self.body = body or b''
        self.headers = headers or {}


# Importing these modules will attach routes to app
from . import controller
from . import keyboard
from . import translations

# Import static last since it is the catch-all route
from . import static
