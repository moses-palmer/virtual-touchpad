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


import os
import pkg_resources
import threading

import PIL.Image

from Xlib import X
from Xlib import display

from virtualtouchpad.platform.xorg import display_manager

from virtualtouchpad import __name__ as PKG_RESOURCES_PACKAGE

from .. import SystemTrayIcon


class SystemTrayIcon(SystemTrayIcon):
    _XEMBED_INFO = '_XEMBED_INFO'
    XEMBED_VERSION = 0
    XEMBED_MAPPED = 1

    _NET_SYSTEM_TRAY_OPCODE = '_NET_SYSTEM_TRAY_OPCODE'
    SYSTEM_TRAY_REQUEST_DOCK = 0

    def _send_message(self, window, message, d1 = 0, d2 = 0, d3 = 0):
        """Sends a generic systray message.

        This method does not trap ``X`` errors; that is up to the caller.

        :param window: An ``X`` window.

        :param int message: The message to send.

        :param int d1: Message specific data.

        :param int d2: Message specific data.

        :param int d3: Message specific data.
        """
        self._display.send_event(self.systray_manager,
            display.event.ClientMessage(
                type = X.ClientMessage,
                client_type = self._display.intern_atom(
                    self._NET_SYSTEM_TRAY_OPCODE),
                window = window.id,
                data = (32, (
                    X.CurrentTime,
                    message,
                    d1, d2, d3))),
            event_mask = X.NoEventMask)

    def _dock_window(self):
        """Docks the window in the systray.

        This method traps ``X`` errors.
        """
        with self.display:
            self._send_message(
                self.systray_manager,
                self.SYSTEM_TRAY_REQUEST_DOCK,
                self.window.id)

    def _get_icon_data(self, width, height):
        """Returns the icon image.

        :param int width: The requested width.

        :param int height: The requested height.

        :return: icon data, which may already be cached
        :rtype: (width, height, data)
        """
        if self._icon_data is None \
                or self._icon_data.size != (width, height):
            self._icon_data = PIL.Image.new(
                'RGB',
                (width, height))
            self._icon_data.paste(self._icon.resize((width, height),
                PIL.Image.ANTIALIAS))

        return self._icon_data

    def _on_event(self, e):
        """The default event handler.

        :param e: The current ``X`` event.

        :raises StopIteration: if e is an ``X.DestroyNotify`` event
        """
        if e and e.type == X.DestroyNotify:
            raise StopIteration()

    def on_expose(self, e):
        geometry = e.window.get_geometry()
        self.window.put_pil_image(self._gc, 0, 0,
            self._get_icon_data(geometry.width, geometry.height))

    def on_buttonpress(self, e):
        self.on_click()

    def _mainloop(self, handlers = {}):
        """The main ``X`` event loop.

        This is blocking, so it should be run in a separate thread.

        This method will break when an event handler raises ``StopIteration``.

        :param handlers: Event handler overrides. The keys are on the format
            ``'on_' + <lower case X event name>``. If a key for an event is
            missing, the corresponding method in self is called. If that does
            not exist, the value for the key ``'on_event'`` is used, and if that
            does not exist a default event handler is called.
        """
        self._display = display.Display()

        with self.display:
            self._dock_window()

        # Find the default handler for events
        default_handler = handlers.get('on_event', self._on_event)

        for e in self.events():
            # The name of the handler function
            handler_name = 'on_' + e.__class__.__name__.lower()

            # Execute the handler; prefer a handler from handlers, then fall
            # back on instance methods, and then fall back on no action
            try:
                handlers.get(
                    handler_name,
                    getattr(self,
                        handler_name,
                        default_handler))(e)
            except StopIteration:
                break

    def __init__(self, description, on_click):
        """Creates a systray tray icon.

        :param str description: A descriptive text to apply to the icon.

        :param callable on_click: A callback for when the systray icon is
            clicked.
        """
        super(SystemTrayIcon, self).__init__(description, on_click)

        self._display = None
        self._window = None

        # Load the icon from ../../../html/img/
        self._icon = PIL.Image.open(
            pkg_resources.resource_stream(
                PKG_RESOURCES_PACKAGE,
                os.path.join(
                    'html', 'img', 'icon196x196.png')))
        self._icon_data = None

        self._thread = threading.Thread(target = self._mainloop)
        self._thread.daemon  = True
        self._thread.start()

    @property
    def display(self):
        """The X display as a context manager that will collect X errors on exit
        and raise a RuntimeError if any errors occurred"""
        # Make sure we have a Display instance
        if self._display is None:
            raise RuntimeError('display not initiated')

        return display_manager(self._display)

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

            self._gc = self._window.create_gc()

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
        """Generates X events until the ``X`` connection is terminated.

        If the ``X`` connection is killed, the last event yielded will be
        ``None``.

        :raises RuntimeError: if the display has not been initiated
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
        """Destroys the system tray icon.
        """
        self._window.destroy()
