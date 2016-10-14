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

import logging
import mimetypes
import os
import email.utils
import sys
import time

import virtualtouchpad.resource as resource

from ._static import static as _static
from . import get, HTTPResponse


#: The root path for static resources
ROOT = '.'

#: The files, in the preferred order, to use as index files
INDEX_FILES = (
    'index.min.xhtml',
    'index.xhtml')


@get('/')
@get('/{filepath:.*}')
async def static(headers, filepath=''):
    path = os.path.join(ROOT, filepath)

    # If the resource is a directory, we try to serve the index file
    if resource.isdir(path):
        for index_file in (
                os.path.join(path, index)
                for index in INDEX_FILES):
            if resource.exists(index_file):
                return _static(headers, index_file)
        return HTTPResponse(status=404)

    return _static(headers, path)
