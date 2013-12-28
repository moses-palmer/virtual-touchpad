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


def key_up(key):
    global DISPLAY

    keycode = DISPLAY.keysym_to_keycode(
        XK.string_to_keysym(key))

    # Release the key
    fake_input(DISPLAY, X.KeyRelease, keycode)
    DISPLAY.sync()


def mouse_down(button):
    global DISPLAY

    # Press the button
    fake_input(DISPLAY, X.ButtonPress, button)
    DISPLAY.sync()


def mouse_up(button):
    global DISPLAY

    # Press the button
    fake_input(DISPLAY, X.ButtonRelease, button)
    DISPLAY.sync()


def mouse_scroll(dx, dy):
    global DISPLAY

    # Vertical scroll
    vbutton = X.Button5 if dy > 0 else X.Button4
    for i in range(abs(dy)):
        fake_input(DISPLAY, X.ButtonPress, vbutton)
        fake_input(DISPLAY, X.ButtonRelease, vbutton)
        DISPLAY.sync()

    # Horizontal scroll
    hbutton = 7 if dx > 0 else 6
    for i in range(abs(dx)):
        fake_input(DISPLAY, X.ButtonPress, hbutton)
        fake_input(DISPLAY, X.ButtonRelease, hbutton)
        DISPLAY.sync()


def mouse_move(dx, dy):
    global DISPLAY

    DISPLAY.warp_pointer(dx, dy)
    DISPLAY.sync()

