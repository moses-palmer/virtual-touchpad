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

def key_down(key):
    """
    Sends a key down event.

    @param key
        The name of the key. This value will be handled just like
        Xlib.XK.string_to_keysym would. Thus, 'A' and 'a' will trigger a press
        of the 'A' key. 'Space' and 'space' will trigger space.
    """
    raise NotImplementedError()


def key_up(key):
    """
    Sends a key up event.

    @param key
        The name of the key. This value is handled just like in key_down.
    @see key_down
    """
    raise NotImplementedError()


def mouse_down(button):
    """
    Presses a mouse button.

    @param button
        The button index.
    """
    raise NotImplementedError()


def mouse_up(button):
    """
    Releases a mouse button.

    @param button
        The button index.
    """
    raise NotImplementedError()


def mouse_scroll(dx, dy):
    """
    Scrolls the mouse wheel.

    @param dx, dy
        The horisontal and vertical offset to scroll.
    """
    raise NotImplementedError()


def mouse_move(dx, dy):
    """
    Moves the mouse pointer.

    @param dx, dy
        The horisontal and vertical offset to move.
    """
    raise NotImplementedError()


def _import_symbols():
    """
    Loads the platform dependent driver and populates the module globals.
    """
    import importlib
    import inspect
    import sys

    # Get the name of the platform and load the driver module
    platform = ''.join(c for c in sys.platform if c.isalpha())
    driver = importlib.import_module(
        '._%s' % platform,
        __package__)

    # Get symbols exported from the driver
    symbols = {}
    for name in dir(driver):
        value = getattr(driver, name)

        # We ignore all private symbols
        if name[0] == '_':
            continue

        # The symbol must exist as a global callable in this module
        old_value = globals().get(name, None)
        if old_value is None:
            continue
        if not callable(old_value):
            raise ImportError(
                'error in %s: symbol <%s> must not be global',
                driver.__name__, name)

        # If the symbol is callable, the function signatures must match
        if callable(value):
            argspec = inspect.getargspec(value)
            old_argspec = inspect.getargspec(old_value)
            if argspec != old_argspec:
                raise ImportError(
                    'error in %s: invalid method signature for <%s>',
                    driver.__name__, name)

        # Replace the global
        value.__doc__ = old_value.__doc__
        globals()[name] = value

_import_symbols()

