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

from aiohttp import web


app = web.Application()


def server(configuration):
    """Creates the actual server instance.

    :param virtualtouchpad.status.Status configuration: The server
        configuration. This has to include at least ``SERVER_HOST`` and
        ``SERVER_PORT``.

    :param address: The address on which to listen.

    :return: a server instance
    """
    class Server(object):
        def __init__(self, configuration):
            self.configuration = configuration

        def serve_forever(self):
            if 'server' in app:
                raise RuntimeError('only one server allowed')

            app['server'] = self
            try:
                web.run_app(
                    app,
                    host=configuration.SERVER_HOST(),
                    port=configuration.SERVER_PORT())
            finally:
                del app['server']

    return Server(configuration)
