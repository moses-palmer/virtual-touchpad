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

import functools
import json
import logging
import types

import bottle

app = bottle.Bottle()


class HTTPResponse(object):
    """A lightweight class to represent an HTTP response.
    """
    def __init__(self, status, body=None, headers=None):
        self.status = status
        self.body = body or ''
        self.headers = headers or {}


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


# Importing these modules will attach routes to app
from . import controller
from . import keyboard
from . import translations

# Import static last since it is the catch-all route
from . import static
