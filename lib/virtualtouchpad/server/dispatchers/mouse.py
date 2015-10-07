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

from virtualtouchpad import event


class Handler(object):
    """A handler for mouse events.
    """
    def down(self, button=1):
        """Triggers a a mouse press event.

        :param int button: The button index.
        """
        event.mouse_down(int(button))

    def up(self, button=1):
        """Triggers a a mouse release event.

        :param int button: The button index.
        """
        event.mouse_up(int(button))

    def scroll(self, dx=0, dy=0):
        """Triggers a mouse scroll event.

        :param int dx: The horisontal offset to scroll.

        :param int dy: The vertical offset to scroll.
        """
        event.mouse_scroll(int(dx), int(dy))

    def move(self, dx=0, dy=0):
        """Triggers a mouse move event.

        :param int dx: The horisontal offset to move.

        :param int dy: The vertical offset to move.
        """
        event.mouse_move(int(dx), int(dy))
