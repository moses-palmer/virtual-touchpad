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
import os

from . import app
from ..util import static_file


@app.get('/translations/<domain>')
def translations(domain):
    accept_language = bottle.request.headers.get('Accept-Language') \
        or 'default'
    languages = sorted((
        (
            language.split(';')[0].strip(),
            float(language.split(';q=')[1]) if ';q=' in language else 1.0)
        for language in accept_language.split(',')),
        key=lambda p: p[1],
        reverse=True) + [('default', 0.0)]

    for language, q in languages:
        path = os.path.join('translations', domain, language + '.js')
        if static_file.exists(path):
            return static_file.get(path)

    return bottle.HTTPResponse(status=404)
