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

import bottle
import logging
import mimetypes
import os
import sys
import time

from . import app
from ..util import static_file


log = logging.getLogger(__name__)


#: The name of the file in every directory used as index
INDEX_MIN_FILE = 'index.min.xhtml'


#: The name of the file in every directory used as index unless the minified
#: version exists
INDEX_FILE = 'index.xhtml'


@app.get('/')
@app.get('/<filepath:path>')
def static(filepath='.'):
    if static_file.isdir(filepath):
        for index_file in (
                os.path.join(filepath, INDEX_MIN_FILE),
                os.path.join(filepath, INDEX_FILE)):
            if static_file.exists(index_file):
                return static(index_file)
        return bottle.HTTPResponse(status=404)

    # Open the file and get its size
    try:
        stream = static_file.open_stream(filepath)
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(0, os.SEEK_SET)
        if bottle.request.method == 'HEAD':
            body = ''
        else:
            body = stream.read()

    except IOError:
        log.exception('File %s does not exist', filepath)
        return bottle.HTTPError(404, 'File does not exist.')

    headers = dict()
    headers['Content-Length'] = size

    # Guess the content type and encoding
    mimetype, encoding = mimetypes.guess_type(filepath)
    if mimetype:
        headers['Content-Type'] = mimetype
    if encoding:
        headers['Content-Encoding'] = encoding

    # Check the file mtime; we use the egg file or the current binary
    try:
        st = os.stat(os.path.join(__file__, os.path.pardir, os.path.pardir))
    except OSError:
        st = os.stat(os.path.abspath(sys.argv[0]))
    last_modified = time.strftime(
        '%a, %d %b %Y %H:%M:%S GMT',
        time.gmtime(st.st_mtime))
    headers['Last-Modified'] = last_modified

    if bottle.request.environ.get('HTTP_IF_MODIFIED_SINCE'):
        if_modified_since = bottle.parse_date(bottle.request.environ.get(
            'HTTP_IF_MODIFIED_SINCE').split(";")[0].strip())
        if if_modified_since is not None \
                and if_modified_since >= int(st.st_mtime):
            headers['Date'] = time.strftime(
                '%a, %d %b %Y %H:%M:%S GMT',
                time.gmtime())
        return bottle.HTTPResponse(status=304, **headers)

    return bottle.HTTPResponse(body, **headers)
