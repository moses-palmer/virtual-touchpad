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


import os
import pkg_resources
import tempfile
import threading
import win32con

from .. import SystemTrayIcon

import virtualtouchpad.platform.win32 as win

try:
    import winxpgui as win32gui
except ImportError:
    import win32gui


class SystemTrayIcon(SystemTrayIcon):
    WINDOW_CLASS_NAME = 'VirtualTouchpadWindow'

    WM_NOTIFY = win32con.WM_USER + 20

    def _add_icon(self):
        """Adds a systray icon.
        """
        if self._notify_id:
            message = win32gui.NIM_MODIFY
        else:
            message = win32gui.NIM_ADD

        self._notify_id = (
            self.window,
            0,
            win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
            self.WM_NOTIFY,
            self.icon,
            self._description)
        win32gui.Shell_NotifyIcon(message, self._notify_id)

    def _delete_icon(self):
        """Deletes a systray icon.

        If the icon has not been added, this method has no effect.
        """
        if not self._notify_id:
            return

        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, self._notify_id)
        self._notify_id = None

    def _on_notify(self, event):
        if event == win32con.WM_LBUTTONDOWN:
            self.on_click()

    def _mainloop(self):
        """The main *win32* event loop.

        This is blocking, so it should be run in a separate thread.
        """
        self._add_icon()
        win32gui.PumpMessages()
        self._delete_icon()

    def __init__(self, description, on_click):
        """Creates a systray tray icon.

        :param str description: A descriptive text to apply to the icon.

        :param callable on_click: A callback for when the systray icon is
            clicked.
        """
        super(SystemTrayIcon, self).__init__(description, on_click)

        self._window = None
        self._notify_id = None

        self._thread = threading.Thread(target=self._mainloop)
        self._thread.daemon = True
        self._thread.start()

    @property
    def icon(self):
        """The *win32* icon handle for the systray icon; the icon will be
        loaded if has not yet been created"""
        if hasattr(self, '_icon'):
            return self._icon

        self._icon = (
            self._icon_from_app() or
            self._icon_from_pkg_resources() or
            self._icon_from_fs())
        return self._icon

    def _icon_from_app(self):
        """Loads the icon as a resource from the currently running application.

        This works only if the application has been packaged with *py2exe*.
        """
        instance = win32gui.GetModuleHandle(None)
        try:
            return win32gui.LoadImage(
                instance,
                win.IDI_MAINICON,
                win32con.IMAGE_ICON,
                0,
                0,
                win32con.LR_DEFAULTSIZE)
        except:
            pass

    def _icon_from_pkg_resources(self):
        """Loads the icon icon data stream using ``pkg_resources``, writes it
        to a temporary file and then loads it as an icon.

        The temporary file is removed afterwards.
        """
        icon_path = os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            os.path.pardir,
            os.path.pardir,
            os.path.pardir,
            os.path.pardir,
            'build',
            'icos',
            'icon-all.ico')
        instance = win32gui.GetModuleHandle(None)
        try:
            with pkg_resources.resource_stream(*win.PATH_MAINICON) as f:
                data = f.read()
            fd, icon_path = tempfile.mkstemp()
            try:
                with os.fdopen(fd, 'wb') as f:
                    f.write(data)
                return win32gui.LoadImage(
                    instance,
                    icon_path,
                    win32con.IMAGE_ICON,
                    0,
                    0,
                    win32con.LR_DEFAULTSIZE | win32con.LR_LOADFROMFILE)
            finally:
                try:
                    os.unlink(icon_path)
                except:
                    pass
        except:
            pass

    def _icon_from_fs(self):
        """Loads the icon from the build directory in the file system.

        This works only if the icon is actually available in the file system.
        """
        icon_path = os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            os.path.pardir,
            os.path.pardir,
            os.path.pardir,
            os.path.pardir,
            'build',
            'icos',
            'icon-all.ico')
        instance = win32gui.GetModuleHandle(None)
        try:
            return win32gui.LoadImage(
                instance,
                icon_path,
                win32con.IMAGE_ICON,
                0,
                0,
                win32con.LR_DEFAULTSIZE | win32con.LR_LOADFROMFILE)
        except:
            pass

    @property
    def window(self):
        """The *win32* window to use as systray icon; the window will be
        created when read unless already created"""
        if self._window:
            return self._window

        # Register the window class
        window_class = win32gui.WNDCLASS()
        window_class.hInstance = win32gui.GetModuleHandle(None)
        window_class.hIcon = self.icon
        window_class.lpszClassName = self.WINDOW_CLASS_NAME
        window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        window_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        window_class.hbrBackground = win32con.COLOR_WINDOW

        # TODO: Create mapping from message to method
        window_class.lpfnWndProc = {
            SystemTrayIcon.WM_NOTIFY: lambda wnd, msg, w, l:
                self._on_notify(l)}
        class_atom = win32gui.RegisterClass(window_class)

        # Create the window
        self._window = win32gui.CreateWindow(
            class_atom,
            self.WINDOW_CLASS_NAME,
            win32con.WS_OVERLAPPED | win32con.WS_SYSMENU, 0, 0,
            win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0, 0,
            window_class.hInstance, None)

        return self._window

    def destroy(self):
        """Removes the systray icon.
        """
        self._delete_icon()
