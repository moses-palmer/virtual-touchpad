# coding=utf-8
# virtual-touchpad
# Copyright (C) 2013-2017 Moses Palmér
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
import urllib
import webbrowser

import PIL.Image
import pystray

from pystray import Menu as menu, MenuItem as item

from .routes._util import generate_access_token
from .translation import _
from . import resource


def create(configuration):
    """Creates the system tray icon.
    """
    def href(path):
        def inner(*args, **kwargs):
            webbrowser.open(urllib.parse.urljoin(
                configuration.SERVER_URL, path))
        return inner

    def access_token_toggle(*args):
        configuration.ACCESS_TOKEN = (
            None if configuration.ACCESS_TOKEN is not None
            else generate_access_token())

    return pystray.Icon(
        __name__,
        title='Virtual Touchpad - {}'.format(
            configuration.SERVER_URL),
        icon=PIL.Image.open(
            resource.open_stream(
                {
                    'darwin': 'icon-dark.png',
                    'linux': 'icon-light.png',
                    'win32': 'icon-light.png'}[sys.platform])),
        menu=menu(
            item(
                _('Connect mobile device...'),
                href('qr')),
            item(
                _('Require access code to connect'),
                access_token_toggle,
                checked=lambda i: bool(configuration.ACCESS_TOKEN)),
            menu.SEPARATOR,
            item(
                _('Exit'),
                lambda icon: icon.server.stop())))
