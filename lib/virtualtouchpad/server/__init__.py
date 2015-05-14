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
import gevent
import geventwebsocket
import json
import logging
import os
import sys
import traceback

from .._info import *
from ..platform import *

from .dispatch import dispatch
from . import static_file

try:
    from geventwebsocket.handler import WebSocketHandler
except ImportError:
    from geventwebsocket import WebSocketHandler


#: The name of the file in every directory used as index
INDEX_MIN_FILE = 'index.min.xhtml'


#: The name of the file in every directory used as index unless the minified
#: version exists
INDEX_FILE = 'index.xhtml'


app = bottle.Bottle()
log = logging.getLogger(__name__)

from . import translations
from . import keyboard
from . import controller


@app.route('/')
@app.route('/<filepath:path>')
def static(filepath = '.'):
    if static_file.isdir(filepath):
        for index_file in (
                os.path.join(filepath, INDEX_MIN_FILE),
                os.path.join(filepath, INDEX_FILE)):
            if static_file.exists(index_file):
                return static_file.get(index_file)
        return bottle.HTTPResponse(status = 404)
    else:
        return static_file.get(filepath)


def main(port, address, log_level):
    global app

    import gevent.pywsgi
    import geventwebsocket
    import sys

    sys.stdout.write('Starting server http://%s:%d/...\n' % (
        address, port))

    from gevent import monkey; monkey.patch_all(thread = False)
    return gevent.pywsgi.WSGIServer(
        ('0.0.0.0', port),
        app,
        handler_class = WebSocketHandler)
