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


@get('/img/qr.svg')
@localhost
async def qr(app, request):
    # Generate a QR code SVG and save it to a stream
    with io.BytesIO() as stream:
        pyqrcode.create(
            app['server'].configuration.SERVER_URL(),
            version=4).svg(
                stream,
                background='white',
                omithw=True)

        return Response(
            status=200,
            body=stream.getvalue(),
            headers={
                'Content-Type': 'image/svg+xml'})
