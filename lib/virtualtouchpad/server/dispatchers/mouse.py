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

from pynput.mouse import Button, Controller


class Handler(object):
    """A handler for mouse events.
    """
    #: The scroll threshold required to actually perform scrolling
    SCROLL_THRESHOLD = 10

    def __init__(self):
        self.d = Controller()
        self.ax = 0
        self.ay = 0

    def down(self, button='left'):
        """Triggers a a mouse press event.

        :param str button: The button name. This must be one of the values
            defined for :class:`pynput.mouse.Button`.
        """
        self.d.press(Button[button])

    def up(self, button='left'):
        """Triggers a a mouse release event.

        :param str button: The button name. This must be one of the values
            defined for :class:`pynput.mouse.Button`.
        """
        self.d.release(Button[button])

    def scroll(self, dx=0, dy=0):
        """Triggers a mouse scroll event.

        :param int dx: The horisontal offset to scroll.

        :param int dy: The vertical offset to scroll.
        """
        self.ax += dx
        self.ay += dy

        # Vertical scroll
        xscroll = int(self.ax // self.SCROLL_THRESHOLD)
        self.ax -= xscroll * self.SCROLL_THRESHOLD

        # Horizontal scroll
        yscroll = int(self.ay // self.SCROLL_THRESHOLD)
        self.ay -= yscroll * self.SCROLL_THRESHOLD

        if xscroll or yscroll:
            self.d.scroll(
                xscroll,
                yscroll)

    def move(self, dx=0, dy=0):
        """Triggers a mouse move event.

        :param int dx: The horisontal offset to move.

        :param int dy: The vertical offset to move.
        """
        self.d.move(int(dx), int(dy))
