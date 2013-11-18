# coding=utf-8
'''
virtual-touchpad
Copyright (C) 2013 Moses Palmér

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

from Xlib import X
from Xlib import XK
from Xlib.display import Display
from Xlib.ext.xtest import fake_input

# The global X display
DISPLAY = Display()

def key_down(key):
    global DISPLAY

    keycode = DISPLAY.keysym_to_keycode(
        XK.string_to_keysym(key))

    # Press the key
    fake_input(DISPLAY, X.KeyPress, keycode)
    DISPLAY.sync()
