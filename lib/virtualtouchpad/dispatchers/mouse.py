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

from ..dispatch import dispatcher

from .. import osevent


@dispatcher
def mouse_down(button = 1):
    """
    Triggers a a mouse press event.

    @param button
        The button index.
    """
    osevent.mouse_down(button)


@dispatcher
def mouse_up(button = 1):
    """
    Triggers a a mouse release event.

    @param button
        The button index.
    """
    osevent.mouse_up(button)


@dispatcher
def mouse_scroll(dx = 0, dy = 0):
    """
    Triggers a mouse scroll event.

    @param dx, dy
        The horisontal and vertical offset to scroll.
    """
    osevent.mouse_scroll(dx, dy)


@dispatcher
def mouse_move(dx = 0, dy = 0):
    """
    Treiggers a mouse move event.

    @param dx, dy
        The horisontal and vertical offset to move.
    """
    osevent.mouse_move(dx, dy)

