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
import logging
import mimetypes
import pkg_resources
import os
import sys
import time

from virtualtouchpad import __name__ as PKG_RESOURCES_PACKAGE


log = logging.getLogger(__name__)


# Set a default value for STATIC_ROOT only if it is accessible
DEFAULT_STATIC_ROOT = os.path.join(
    os.path.dirname(__file__),
    os.path.pardir,
    'html')
STATIC_ROOT = os.getenv('VIRTUAL_TOUCHPAD_STATIC_ROOT',
    DEFAULT_STATIC_ROOT if os.access(DEFAULT_STATIC_ROOT, os.R_OK)
    else None)


def exists(path):
    """Returns whether a static file exists.

    :param str path: The path of the static file.
    """
    if not STATIC_ROOT is None:
        # If VIRTUAL_TOUCHPAD_STATIC_ROOT is set, simply check whether we can
        # read the file
        return os.access(os.path.join(STATIC_ROOT, path), os.R_OK)

    # Otherwise, check with pkg_resource
    return pkg_resources.resource_exists(
        PKG_RESOURCES_PACKAGE, os.path.join('html', path))


def isdir(path):
    """Returns whether a static file exists and is a directory.

    :param str path: The path of the static file.
    """
    if not STATIC_ROOT is None:
        # If VIRTUAL_TOUCHPAD_STATIC_ROOT is set, simply check whether we can
        # read the file
        return os.path.isdir(os.path.join(STATIC_ROOT, path))

    # Otherwise, check with pkg_resource
    return pkg_resources.resource_isdir(
        PKG_RESOURCES_PACKAGE, os.path.join('html', path))


def list(path):
    """Lists all resources available under ``path``.

    :param str path: The path to check.

    :return: a list of resources
    :rtype: [str]
    """
    if not STATIC_ROOT is None:
        return os.listdir(os.path.join(STATIC_ROOT, path))

    return pkg_resources.resource_listdir(PKG_RESOURCES_PACKAGE,
        os.path.join('html', path))


def get(path):
    """Returns a :class:`bottle.HTTPResponse` or :class:`bottle.HTTPError`
    containing either the file requested or an error message.

    :param str path: The path of the static file.
    """
    if not STATIC_ROOT is None:
        # If VIRTUAL_TOUCHPAD_STATIC_ROOT is set, simply use bottle
        return bottle.static_file(path, root = STATIC_ROOT)

    # Otherwise, try to serve a resource from the egg
    try:
        path = pkg_resources.resource_filename(
                PKG_RESOURCES_PACKAGE, os.path.join('html', path))
        return bottle.static_file(
            os.path.basename(path), root = os.path.dirname(path))
    except KeyError:
        # The file does not exist; we try to serve a file that we are
        # certain does not exist to trigger a 404
        return bottle.static_file(
            path, root = os.path.join(os.path.dirname(__file__), 'html'))
    except NotImplementedError:
        # pkg_resources does not support resource_filename when running from
        # a zip file
        if hasattr(sys, 'frozen'):
            pass
        else:
            raise

    # Open the file and get its size
    try:
        stream = pkg_resources.resource_stream(PKG_RESOURCES_PACKAGE,
                os.path.join('html', path))
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(0, os.SEEK_SET)
        if bottle.request.method == 'HEAD':
            body = ''
        else:
            body = stream.read()
    except IOError:
        log.exception('File %s does not exist', path)
        return bottle.HTTPError(404, 'File does not exist.')

    headers = dict()
    headers['Content-Length'] = size

    # Guess the content type and encoding
    mimetype, encoding = mimetypes.guess_type(path)
    if mimetype:
        headers['Content-Type'] = mimetype
    if encoding:
        headers['Content-Encoding'] = encoding

    # Check the file mtime; we use the egg file or the current binary
    try:
        st = os.stat(os.path.join(__file__, os.path.pardir, os.path.pardir))
    except OSError:
        st = os.stat(os.path.abspath(sys.argv[0]))
    last_modified = time.strftime('%a, %d %b %Y %H:%M:%S GMT',
        time.gmtime(st.st_mtime))
    headers['Last-Modified'] = last_modified

    if bottle.request.environ.get('HTTP_IF_MODIFIED_SINCE'):
        if_modified_since = bottle.parse_date(bottle.request.environ.get(
            'HTTP_IF_MODIFIED_SINCE').split(";")[0].strip())
        if not if_modified_since is None \
                and if_modified_since >= int(st.st_mtime):
            headers['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT",
                time.gmtime())
        return bottle.HTTPResponse(status = 304, **headers)

    return bottle.HTTPResponse(body, **headers)
