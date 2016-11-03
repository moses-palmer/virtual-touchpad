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

import json
import logging
import os

from aiohttp.web import HTTPNotFound

import virtualtouchpad.resource as resource

from . import get
from ._util import static


log = logging.getLogger(__name__)


#: The root path for layouts
ROOT = 'keyboard/layout'


@get('/keyboard/layout/default')
async def default_layout(app, headers):
    """Returns the default keyboard layout.
    """
    layout_files = resource.list(ROOT)
    if not layout_files:
        raise HTTPNotFound()

    # TODO: Select the one used by the current system
    with resource.open_stream(os.path.join(ROOT, layout_files[0])) as f:
        return json.loads(f.read().decode('utf-8'))


@get('/keyboard/layout/')
async def list_layouts(app, headers):
    """Returns a list of all keyboard layouts.
    """
    layout_files = resource.list(ROOT)
    if not layout_files:
        raise HTTPNotFound()

    layouts = []
    for layout_file in layout_files:
        path = '%s/%s' % (ROOT, layout_file)
        try:
            with resource.open_stream(path) as f:
                layout = json.loads(f.read().decode('utf-8'))
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
