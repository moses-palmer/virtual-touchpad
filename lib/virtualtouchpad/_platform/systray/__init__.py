# coding=utf-8
'''
virtual-touchpad
Copyright (C) 2013-2014 Moses Palmér

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
'''


class SystemTrayIcon(object):
    """
    An object representing a system tray icon.
    """

    def __init__(self, description):
        """
        Creates a new system tray icon.

        @param description
            The short description of this system tray icon.
        """
        self._description = description

    @property
    def description(self):
        """The short description of this system tray icon"""
        return self._description


def create(description):
    """
    Creates a systray icon with a text.

    @param description
        The text used to describe the systray icon.
    @return a context
    """
    raise NotImplementedError()


def destroy(context):
    """
    Deletes a systray icon

    @param context
        The context returned by systray_create
    @see create
    """
    raise NotImplementedError()


from .. import _import_symbols
_import_symbols(globals())
