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
import json
import logging

from . import app
from ..util import static_file


log = logging.getLogger(__name__)


#: The root path for layouts
ROOT = 'keyboard/layout'


@app.get('/keyboard/layout/default')
def default_layout():
    """Returns the default keyboard layout.
    """
    layout_files = static_file.list(ROOT)
    if not layout_files:
        return bottle.HTTPResponse(status=404)

    # TODO: Select the one used by the current system
    return static_file.get('%s/%s' % (ROOT, layout_files[0]))


@app.get('/keyboard/layout/')
def list_layouts():
    """Returns a list of all keyboard layouts.
    """
    layout_files = static_file.list(ROOT)
    if not layout_files:
        return bottle.HTTPResponse(status=404)

    layouts = []
    for layout_file in layout_files:
        path = '%s/%s' % (ROOT, layout_file)
        try:
            with static_file.open_stream(path) as f:
                layout = json.load(f)
                layouts.append({
                    'url': '/%s' % path,
                    'name': layout['meta']['name']})
        except IOError:
            log.exception('Failed to open %s', path)
        except ValueError:
            log.exception('Failed to load JSON value from %s', path)
        except:
            log.exception('wha?')

    return {
        'layouts': layouts}
