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

from virtualtouchpad import platform
with platform.modules():
    import Xlib.keysymdef.xkb

    from Xlib import display
    from Xlib import X
    from Xlib import XK
    from Xlib.ext.xtest import fake_input

    try:
        import pyatspi
    except ImportError:
        pyatspi = None


from virtualtouchpad.platform.xorg import display_manager


#: The global X display
DISPLAY = display.Display()


# The scroll threshold required to actually perform scrolling
SCROLL_THRESHOLD = 10

# The thresholds for movements
SHRT_MAX = 32767
SHRT_MIN = -SHRT_MAX - 1

# The accumulated scrolling
scroll = [0, 0]


def mouse_scroll_cancel():
    """Cancels any scrolling in progress.
    """
    global scroll
    scroll = [0, 0]


def string_to_keysym(key, default = None):
    """Converts a string to a keysym identifier.

    :param str keysym: The string to convert.

    :return: the corresponding key identifier
    :rtype: int

    :raises ValueError: if the string is unknown
    """
    keysym = XK.string_to_keysym(key)
    if not keysym:
        keysym = getattr(Xlib.keysymdef.xkb, 'XK_' + key, default)
    if not keysym:
        raise ValueError('invalid symbol: %s', key)
    return keysym


def key_down(name, keysym, symbol):
    # Convert the symbol name to an identifier
    keysym = string_to_keysym(symbol, keysym)

    with display_manager(DISPLAY) as display:
        # Press the key
        keycode = display.keysym_to_keycode(keysym)
        fake_input(display, X.KeyPress, keycode)


def key_up(name, keysym, symbol):
    # Convert the symbol name to an identifier
    keysym = string_to_keysym(symbol, keysym)

    with display_manager(DISPLAY) as display:
        # Release the key
        keycode = display.keysym_to_keycode(keysym)
        fake_input(display, X.KeyRelease, keycode)


def mouse_down(button):
    with display_manager(DISPLAY) as display:
        mouse_scroll_cancel()

        # Press the button
        fake_input(display, X.ButtonPress, button)


def mouse_up(button):
    with display_manager(DISPLAY) as display:
        mouse_scroll_cancel()

        # Press the button
        fake_input(display, X.ButtonRelease, button)


def mouse_scroll(dx, dy):
    global SCROLL_THRESHOLD
    global scroll

    scroll[0] += dx
    scroll[1] += dy

    with display_manager(DISPLAY) as display:
        # Vertical scroll
        vscroll = scroll[1] // SCROLL_THRESHOLD
        if vscroll > 0:
            vbutton = X.Button5
        elif vscroll < 0:
            vbutton = X.Button4
        for i in range(abs(vscroll)):
            fake_input(display, X.ButtonPress, vbutton)
            fake_input(display, X.ButtonRelease, vbutton)
        scroll[1] -= vscroll * SCROLL_THRESHOLD

        # Horizontal scroll
        hscroll = scroll[0] // SCROLL_THRESHOLD
        if hscroll > 0:
            hbutton = 7
        elif hscroll < 0:
            hbutton = 6
        for i in range(abs(hscroll)):
            fake_input(display, X.ButtonPress, hbutton)
            fake_input(display, X.ButtonRelease, hbutton)
        scroll[0] -= hscroll * SCROLL_THRESHOLD


def mouse_move(dx, dy):
    with display_manager(DISPLAY) as display:
        mouse_scroll_cancel()

        # The movement is a short
        dx = max(min(dx, SHRT_MAX), SHRT_MIN)
        dy = max(min(dy, SHRT_MAX), SHRT_MIN)

        if pyatspi:
            pyatspi.Registry.generateMouseEvent(dx, dy, 'rel')
        else:
            display.warp_pointer(dx, dy)
