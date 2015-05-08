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


class SystemTrayIcon(object):
    """An object representing a system tray icon.
    """

    def __init__(self, description, on_click):
        """Creates a new system tray icon.

        :param str description: The short description of this system tray icon.

        :param callable on_click: A callback for when the systray icon is
            clicked.
        """
        self._description = description
        self._on_click = on_click

    @property
    def description(self):
        """The short description of this system tray icon"""
        return self._description

    def on_click(self):
        if self._on_click:
            self._on_click()


from virtualtouchpad.platform import implement
implement(globals())
