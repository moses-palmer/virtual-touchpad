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


from .._info import *

from .._platform import *

import gevent

import bottle
import geventwebsocket
import json
import mimetypes
import os
import pkg_resources
import sys
import time

try:
    from geventwebsocket.handler import WebSocketHandler
except ImportError:
    from geventwebsocket import WebSocketHandler

from ..dispatch import dispatch

app = bottle.Bottle()


# Set a default value for STATIC_ROOT only if it is accessible
DEFAULT_STATIC_ROOT = os.path.join(
    os.path.dirname(__file__),
    os.path.pardir,
    'html')
STATIC_ROOT = os.getenv('VIRTUAL_TOUCHPAD_STATIC_ROOT',
    DEFAULT_STATIC_ROOT if os.access(DEFAULT_STATIC_ROOT, os.R_OK)
    else None)


@app.route('/translations/<domain>')
def translations(domain):
    accept_language = bottle.request.headers.get('Accept-Language') or 'default'
    languages = sorted((
        (
            language.split(';')[0].strip(),
            float(language.split(';q=')[1]) if ';q=' in language else 1.0)
        for language in accept_language.split(',')),
        key = lambda p: p[1],
        reverse = True) + [('default', 0.0)]

    for language, q in languages:
        path = os.path.join('translations', domain, language + '.js')
        if static_file_exists(path):
            return static_file(path)

    return bottle.HTTPResponse(status = 404)


@app.route('/ws')
def handle_websocket():
    # Get the actual websocket
    ws = bottle.request.environ.get('wsgi.websocket')
    if not ws:
        bottle.abort(400, 'Expected WebSocket request.')

    while True:
        try:
            message = ws.receive()
            if message is None:
                break

            try:
                command = json.loads(message)
                dispatch(command)

            except (KeyError, ValueError, TypeError):
                bottle.abort(400, 'Invalid command')

        except geventwebsocket.WebSocketError:
            break


def static_file_exists(path):
    """Returns whether a static file exists.

    :param str path: The path of the static file.
    """
    if not STATIC_ROOT is None:
        # If VIRTUAL_TOUCHPAD_STATIC_ROOT is set, simply check whether we can
        # read the file
        return os.access(os.path.join(STATIC_ROOT, path), os.R_OK)
    else:
        # Otherwise, check with pkg_resource
        return pkg_resources.resource_exists(
                    __name__, os.path.join('html', path))


def static_file(path):
    """Returns a :class:`bottle.HTTPResponse` or :class:`bottle.HTTPError`
    containing either the file requested or an error message.

    :param str path: The path of the static file.
    """
    if not STATIC_ROOT is None:
        # If VIRTUAL_TOUCHPAD_STATIC_ROOT is set, simply use bottle
        return bottle.static_file(path, root = STATIC_ROOT)
    else:
        # Otherwise, try to serve a resource from the egg
        try:
            path = pkg_resources.resource_filename(
                    __name__, os.path.join('html', path))
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
        stream = pkg_resources.resource_stream(__name__,
                os.path.join('html', path))
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(0, os.SEEK_SET)
        if bottle.request.method == 'HEAD':
            body = ''
        else:
            body = stream.read()
    except IOError:
        return bottle.HTTPError(404, 'File does not exist.')

    headers = dict()
    headers['Content-Length'] = size

    # Guess the content type and encoding
    mimetype, encoding = mimetypes.guess_type(path)
    if mimetype:
        headers['Content-Type'] = mimetype
    if encoding:
        headers['Content-Encoding'] = encoding

    # Check the file mtime; we use the egg file
    st = os.stat(os.path.join(__file__, os.path.pardir, os.path.pardir))
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


@app.route('/<filepath:path>')
def static(filepath):
    return static_file(filepath)


@app.route('/')
def index():
    return static('index.xhtml')


MINIFIED_XHTML = 'index.min.xhtml'
if static_file_exists(MINIFIED_XHTML):
    @app.route('/')
    def index_minified():
        return static(MINIFIED_XHTML)


def main(port, address):
    global app

    import gevent.pywsgi
    import geventwebsocket
    import sys

    name, host = address

    sys.stdout.write('Starting server http://%s:%d/...\n' % (
        name, port))

    from gevent import monkey; monkey.patch_all(thread = False)
    return gevent.pywsgi.WSGIServer(
        (host, port),
        app,
        handler_class = WebSocketHandler)
