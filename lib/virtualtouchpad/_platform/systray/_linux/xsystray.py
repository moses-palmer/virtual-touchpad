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

from virtualtouchpad._platform._linux import *


class XSystemTrayIcon(object):
    def __init__(self, description):
        """
        Creates a systray tray icon.

        @param description
            A descriptive text to apply to the icon.
        """
        self._description = description
        self._display = None

    @property
    def display(self):
        """The X display as a context manager that will collect X errors on exit
        and raise a RuntimeError if any errors occurred"""
        # Make sure we have a Display instance
        if self._display is None:
            raise RuntimeError('display not initiated')

        from contextlib import contextmanager

        @contextmanager
        def manager():
            errors = []
            old_handler = self._display.set_error_handler(errors.append)
            yield self._display
            self._display.sync()
            self._display.set_error_handler(old_handler)
            if errors:
                raise RuntimeError(errors)

        return manager()

    def destroy(self):
        """
        Destroys the system tray icon.
        """
        # TODO: Implement
        pass
