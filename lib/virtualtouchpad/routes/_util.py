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

import email.utils
import logging
import mimetypes
import os
import sys
import time

from aiohttp.web import HTTPFound, HTTPNotFound, Response

import virtualtouchpad.resource as resource


#: The root directory, relative to the path in virtualtouchpad.resource, of the
#: static files
ROOT = '.'


log = logging.getLogger(__name__)


def read(root, filepath):
    """Reads a file and guesses the content type.

    :param str root: The root path to which `filepath` is a relative path.

    :param str filepath: The resource path.

    :return: the tuple ``(headers, body)``

    :raises aiohttp.web.HTTPFound: if ``path`` is a directory, but does not end
        with ``'/'``
    """
    path = os.path.join(root, filepath)

    # Redirect to directories
    if resource.isdir(path) and path[-1] != '/':
        raise HTTPFound(filepath + '/')

    # Read the file
    body = resource.open_stream(path).read()

    # Guess the content type and encoding
    headers = {}
    mimetype, encoding = mimetypes.guess_type(path)
    if mimetype:
        headers['Content-Type'] = mimetype
    if encoding:
        headers['Content-Encoding'] = encoding

    return headers, body


def static(headers, root, filepath='.'):
    """Reads a static file and returns a response object.

    If the file cannot be opened, ``None`` is returned.

    This function honours the ``If-Modified-Since`` header.

    :param headers: The request headers. These are used to decide whether to
        return ``HTTP 304`` when requesting a file the second time.

    :param str root: The root path to which `filepath` is a relative path.

    :param str filepath: The path of the resource. The resource is read using
        :func:`virtualtouchpad.resource.open_stream`.

    :return: a response

    :raises HTTPNotFound: if the resource does not exist
    """
    fullroot = os.path.join(ROOT, root)

    # Open the file and get its size
    try:
        response_headers, body = read(fullroot, filepath)

    except FileNotFoundError:
        log.warn('File %s does not exist', filepath)
        raise HTTPNotFound()

    response_headers['Content-Length'] = len(body)

    # Check the file mtime; we use the egg file or the current binary
    try:
        st = os.stat(os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            os.path.pardir))
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
        return Response(status=304, headers=response_headers)

    return Response(status=200, body=body, headers=response_headers)
