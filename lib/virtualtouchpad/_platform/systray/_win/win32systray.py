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

import os
import sys
import win32api
import win32con
import win32gui_struct
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui

import  virtualtouchpad._platform._win as _win


class Win32SystemTrayIcon(object):
    WINDOW_CLASS_NAME = 'VirtualTouchpadWindow'

    def __init__(self, description):
        """
        Creates a systray tray icon.

        @param description
            A descriptive text to apply to the icon.
        """
        self._description = description

        self._icon = None
        self._window = None

    @property
    def icon(self):
        """The Win32 icon handle for the systray icon; the icon will be loaded
        if has not yet been created"""
        if self._icon:
            return self._icon

        # First try to load from the current EXE file, and then fall back on the
        # build directory
        instance = win32gui.GetModuleHandle(None)
        try:
            self._icon = win32gui.LoadImage(
                instance,
                _win.IDI_MAINICON,
                win32con.IMAGE_ICON,
                0,
                0,
                win32con.LR_DEFAULTSIZE)
        except:
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
            self._icon = win32gui.LoadImage(
                instance,
                icon_path,
                win32con.IMAGE_ICON,
                0,
                0,
                win32con.LR_DEFAULTSIZE | win32con.LR_LOADFROMFILE)
        return self._icon

    @property
    def window(self):
        """The Win32 window to use as systray icon; the window will be created
        when read unless already created"""
        if self._window:
            return self._window

        # Register the window class
        window_class = win32gui.WNDCLASS()
        window_class.hInstance = win32gui.GetModuleHandle(None)
        window_class.hIcon = self.icon
        window_class.lpszClassName = self.WINDOW_CLASS_NAME
        window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
        window_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        window_class.hbrBackground = win32con.COLOR_WINDOW

        # TODO: Create mapping from message to method
        window_class.lpfnWndProc = {}
        class_atom = win32gui.RegisterClass(window_class)

        # Create the window
        self._window = win32gui.CreateWindow(class_atom,
            self.WINDOW_CLASS_NAME,
            win32con.WS_OVERLAPPED | win32con.WS_SYSMENU, 0, 0,
            win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0, 0,
            window_class.hInstance, None)

        return self._window
