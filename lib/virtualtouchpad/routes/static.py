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

import logging
import mimetypes
import os
import email.utils
import sys
import time

import virtualtouchpad.resource as resource

from . import get, HTTPResponse


log = logging.getLogger(__name__)

#: The files, in the preferred order, to use as index files
INDEX_FILES = (
    'index.min.xhtml',
    'index.xhtml')


@get('/')
@get('/<filepath:path>')
def static(headers, filepath='.'):
    # If the resource is a directory, we try to serve the index file
    if resource.isdir(filepath):
        for index_file in (
                os.path.join(filepath, index) for index in INDEX_FILES):
            if resource.exists(index_file):
                return static(headers, index_file)
        return HTTPResponse(404)

    # Open the file and get its size
    try:
        stream = resource.open_stream(filepath)
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(0, os.SEEK_SET)
        body = stream.read()

    except IOError:
        log.exception('File %s does not exist', filepath)
        return HTTPResponse(404)

    response_headers = {}
    response_headers['Content-Length'] = size

    # Guess the content type and encoding
    mimetype, encoding = mimetypes.guess_type(filepath)
    if mimetype:
        response_headers['Content-Type'] = mimetype
    if encoding:
        response_headers['Content-Encoding'] = encoding

    # Check the file mtime; we use the egg file or the current binary
    try:
        st = os.stat(os.path.join(__file__, os.path.pardir, os.path.pardir))
    except OSError:
        st = os.stat(os.path.abspath(sys.argv[0]))
    response_headers['Last-Modified'] = email.utils.formatdate(st.st_mtime)

    if headers.get('if-modified-since'):
        if_modified_since = time.mktime(email.utils.parsedate(
            headers.get('if-modified-since').split(";")[0].strip()))
        if if_modified_since is not None \
                and if_modified_since >= int(st.st_mtime):
            response_headers['Date'] = time.strftime(
                '%a, %d %b %Y %H:%M:%S GMT',
                time.gmtime())
        return HTTPResponse(304, headers=response_headers)

    return HTTPResponse(200, body=body, headers=response_headers)
