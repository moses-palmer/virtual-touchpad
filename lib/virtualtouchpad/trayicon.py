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

import sys

import PIL.Image
import pystray

from pystray import Menu as menu, MenuItem as item

from .translation import _
from . import resource


def create(configuration):
    """Creates the system tray icon.
    """
    return pystray.Icon(
        __name__,
        title='Virtual Touchpad - {}'.format(
            configuration.SERVER_URL()),
        icon=PIL.Image.open(
            resource.open_stream(
                {
                    'darwin': 'icon-dark.png',
                    'linux': 'icon-light.png',
                    'win32': 'icon-light.png'}[sys.platform])),
        menu=menu(
            item(
                _('Exit'),
                lambda icon: icon.server.stop())))
