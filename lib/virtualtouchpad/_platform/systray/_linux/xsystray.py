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

import threading

from virtualtouchpad._platform._linux import *


class XSystemTrayIcon(object):
    _XEMBED_INFO = '_XEMBED_INFO'
    XEMBED_VERSION = 0
    XEMBED_MAPPED = 1

    def __init__(self, description):
        """
        Creates a systray tray icon.

        @param description
            A descriptive text to apply to the icon.
        """
        self._description = description
        self._display = None
        self._window = None

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

    @property
    def window(self):
        """The X window to use as systray icon; the window will be created when
        read unless already created"""
        if self._window:
            return self._window

        with self.display as display:
            # Create the window
            screen = display.screen()
            self._window = screen.root.create_window(
                -1, -1, 1, 1, 0, screen.root_depth,
                event_mask = X.ExposureMask,
                window_class = X.InputOutput)
            self._window.set_wm_class(
                'VirtualTouchpadSystemTrayIcon',
                'VirtualTouchpad')
            self._window.set_wm_name(
                self._description)

            # Enable XEMBED for the window
            atom = display.intern_atom(self._XEMBED_INFO)
            self._window.change_property(atom, atom, 32, [
                self.XEMBED_VERSION,
                self.XEMBED_MAPPED])

        return self._window

    @property
    def systray_manager(self):
        """The X window that owns the systray selection, or None if no window
        does"""
        while True:
            with self.display as display:
                display.grab_server()
                systray_manager = display.get_selection_owner(
                    display.intern_atom(
                        '_NET_SYSTEM_TRAY_S%d' % display.get_default_screen()))
                display.ungrab_server()
                display.flush()

                if systray_manager != X.NONE:
                    return display.create_resource_object(
                        'window',
                        systray_manager.id)

                # TODO: Wait for a systray manager to appear
                break

    def events(self):
        """
        Generates X events until the X connection is terminated.

        If the X connection is killed, the last event yielded will be None.

        @raise RuntimeError if the display has not been initiated
        """
        if self._display is None:
            raise RuntimeError('display not initiated')

        while True:
            # Read the next event or silently exit
            try:
                e  = self._display.next_event()
            except:
                e = None

            yield e

            if e is None:
                break

    def destroy(self):
        """
        Destroys the system tray icon.
        """
        self._window.destroy()
