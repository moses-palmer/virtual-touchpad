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

import bottle

app = bottle.Bottle()


def main(port, address, log_level):
    import gevent.pywsgi
    import sys

    try:
        from geventwebsocket.handler import WebSocketHandler
    except ImportError:
        from geventwebsocket import WebSocketHandler

    # Importing this module will attach routes to app
    from . import routes

    sys.stdout.write('Starting server http://%s:%d/...\n' % (
        address, port))

    from gevent import monkey
    monkey.patch_all(thread=False)
    return gevent.pywsgi.WSGIServer(
        ('0.0.0.0', port),
        app,
        handler_class=WebSocketHandler)
