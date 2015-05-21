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

from . import app
from .. import static_file


@app.get('/keyboard/layout/default')
def default_layout():
    """Returns the default keyboard layout.
    """
    geometry_files = static_file.list('keyboard/layout')
    if not geometry_files:
        return bottle.HTTPResponse(status = 404)

    # TODO: Select the one used by the current system
    return static_file.get('keyboard/layout/' + geometry_files[0])
