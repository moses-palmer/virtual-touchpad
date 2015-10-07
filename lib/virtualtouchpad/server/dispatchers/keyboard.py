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
    def __init__(self):
        self.state = None

    def down(self, name, keysym, symbol):
        """Triggers a key down event.

        :param str name: The name of the key. This should typically be the
            actual character requested, or ``None``.

        :param int keysym: The keysym identifier of the key that is being
            pressed. This value will be passed directly to
            :func:`event.key_down`.

            If ``symbol`` is a valid value, this parameter will be ignored.

        :param str symbol: The symbol name of the key that is being pressed.
            This value will be passed directly to :func:`event.key_down`.
        """
        self.state = event.key_down(self.state, name, keysym, symbol)

    def up(self, name, keysym, symbol):
        """Triggers a key up event.

        :param str name: The name of the key. This should typically be the
            actual character requested, or ``None``.

        :param int keysym: The keysym identifier of the key that is being
            released. This value will be passed directly to
            :func:`event.key_up`.

            If ``symbol`` is a valid value, this parameter will be ignored.

        :param str symbol: The symbol name of the key that is being released.
            This value will be passed directly to :func:`event.key_up`.
        """
        self.state = event.key_up(self.state, name, keysym, symbol)
