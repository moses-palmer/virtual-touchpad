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

import os

from aiohttp.web import HTTPNotFound

import virtualtouchpad.resource as resource

from ._util import static
from . import get


#: The root path for static resources
ROOT = 'html'

#: The files, in the preferred order, to use as index files
INDEX_FILES = (
    'index.xhtml.min',
    'index.xhtml')


@get('/')
@get('/{filepath:.*}')
async def file_resource(headers, filepath=''):
    # If the resource is a directory, we try to serve the index file
    if resource.isdir(os.path.join(ROOT, filepath)):
        for index_file in (
                os.path.join(filepath, index)
                for index in INDEX_FILES):
            if resource.exists(os.path.join(ROOT, index_file)):
                return static(headers, ROOT, index_file)
        raise HTTPNotFound()

    return static(headers, ROOT, filepath)
