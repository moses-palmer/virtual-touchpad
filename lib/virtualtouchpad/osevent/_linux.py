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

from Xlib import X
from Xlib import XK
from Xlib.display import Display
from Xlib.ext.xtest import fake_input

try:
    import pyatspi
except ImportError:
    pyatspi = None

# The global X display
DISPLAY = Display()


# The scroll threshold required to actually perform scrolling
SCROLL_THRESHOLD = 10

# The accumulated scrolling
scroll = [0, 0]

def mouse_scroll_cancel():
    """
    Cancels any scrolling in progress.
    """
    global scroll
    scroll = [0, 0]


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

    mouse_scroll_cancel()

    # Press the button
    fake_input(DISPLAY, X.ButtonPress, button)
    DISPLAY.sync()


def mouse_up(button):
    global DISPLAY

    mouse_scroll_cancel()

    # Press the button
    fake_input(DISPLAY, X.ButtonRelease, button)
    DISPLAY.sync()


def mouse_scroll(dx, dy):
    global DISPLAY
    global SCROLL_THRESHOLD
    global scroll

    scroll[0] += dx
    scroll[1] += dy

    # Vertical scroll
    vscroll = scroll[1] // SCROLL_THRESHOLD
    if vscroll > 0:
        vbutton = X.Button5
    elif vscroll < 0:
        vbutton = X.Button4
    for i in range(abs(vscroll)):
        fake_input(DISPLAY, X.ButtonPress, vbutton)
        fake_input(DISPLAY, X.ButtonRelease, vbutton)
    scroll[1] -= vscroll * SCROLL_THRESHOLD

    # Horizontal scroll
    hscroll = scroll[0] // SCROLL_THRESHOLD
    if hscroll > 0:
        hbutton = 7
    elif hscroll < 0:
        hbutton = 6
    for i in range(abs(hscroll)):
        fake_input(DISPLAY, X.ButtonPress, hbutton)
        fake_input(DISPLAY, X.ButtonRelease, hbutton)
    scroll[0] -= hscroll * SCROLL_THRESHOLD

    if vscroll or hscroll:
        DISPLAY.sync()


def mouse_move(dx, dy):
    global DISPLAY

    mouse_scroll_cancel()

    if pyatspi:
        pyatspi.Registry.generateMouseEvent(dx, dy, 'rel')
    else:
        DISPLAY.warp_pointer(dx, dy)
        DISPLAY.sync()
