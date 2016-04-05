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

from aiohttp import web


app = web.Application()


def server(port, address):
    """Creates the actual server instance.

    :param int port: The port on which to listen.

    :param address: The address on which to listen.

    :return: a server instance
    """
    class Server(object):
        def serve_forever(self):
            web.run_app(app, host=address, port=port)

    return Server()
