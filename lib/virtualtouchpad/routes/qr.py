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

import io

from . import get, localhost

import pyqrcode

from aiohttp.web import Response


def url(configuration):
    """Generates the URL to use for connecting.

    :param configuration: The server configuration.

    :return: a URL
    """
    access_token = configuration.ACCESS_TOKEN
    if access_token is None:
        return configuration.SERVER_URL
    else:
        return '%s#%s' % (configuration.SERVER_URL, access_token)


@get('/img/qr.svg')
@localhost
async def qr(app, request):
    # Generate a QR code SVG and save it to a stream; we need at least version 8
    # for the QR code
    with io.BytesIO() as stream:
        pyqrcode.create(
            url(app['server'].configuration),
            version=8).svg(
                stream,
                background='white',
                omithw=True)

        return Response(
            status=200,
            body=stream.getvalue(),
            headers={
                'Content-Type': 'image/svg+xml'})
