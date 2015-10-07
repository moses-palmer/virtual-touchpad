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

from virtualtouchpad.platform import implement


def key_down(state, name, keysym, symbol):
    """Sends a key down event.

    :param state: The current keyboard state. This is an opaque value used by
        the backend.

    :param str name: The name of the key. This should typically be the actual
        character requested, or ``None``.

    :param int keysym: The key symbol identifier of the key being pressed.

    :param str symbol: The symbol name of the key. This value will be handled
        just like :func:`Xlib.XK.string_to_keysym` would. Thus, ``'A'`` and
        ``'a'`` will trigger a press of the ``'A'`` key. ``'Space'`` and
        ``'space'`` will trigger space.

    :return: the new state
    """
    raise NotImplementedError()


def key_up(state, name, keysym, symbol):
    """Sends a key up event.

    :param state: The current keyboard state. This is an opaque value used by
        the backend.

    :param str name: The name of the key. This should typically be the actual
        character requested, or ``None``.

    :param int keysym: The key symbol identifier of the key being pressed.

    :param str symbol: The symbol name of the key. This value will be handled
        just like :func:`Xlib.XK.string_to_keysym` would. Thus, ``'A'`` and
        ``'a'`` will trigger a press of the ``'A'`` key. ``'Space'`` and
        ``'space'`` will trigger space.

    :return: the new state
    """
    raise NotImplementedError()


def mouse_down(state, button):
    """Presses a mouse button.

    :param state: The current mouse state. This is an opaque value used by the
        backend.

    :param int button: The button index.

    :return: the new state
    """
    raise NotImplementedError()


def mouse_up(state, button):
    """Releases a mouse button.

    :param state: The current mouse state. This is an opaque value used by the
        backend.

    :param int button: The button index.

    :return: the new state
    """
    raise NotImplementedError()


def mouse_scroll(state, dx, dy):
    """Scrolls the mouse wheel.

    :param state: The current mouse state. This is an opaque value used by the
        backend.

    :param int dx: The horisontal offset to scroll.

    :param int dy: The vertical offset to scroll.

    :return: the new state
    """
    raise NotImplementedError()


def mouse_move(state, dx, dy):
    """Moves the mouse pointer.

    :param state: The current mouse state. This is an opaque value used by the
        backend.

    :param int dx: The horisontal offset to move.

    :param int dy: The vertical offset to move.

    :return: the new state
    """
    raise NotImplementedError()


implement(globals())
