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

from pynput.keyboard import KeyCode, Key, Controller


class Handler(object):
    def __init__(self):
        self.d = Controller()

    def keycode(self, name, is_dead):
        """Resolves a key description to a value that can be passed to
        :meth:`pynput.keyboard.Controller.press` and
        :meth:`~pynput.keyboard.Controller.release`.

        :param str name: The name of the key. This should typically be the
            actual character requested. If it starts with ``'<'`` and ends with
            ``'>'``, the key value is looked up in
            :class:`pynput.keyboard.Key`, otherwise it is passed straight to
            :meth:`pynput.keyboard.Controller.press`.

        :return: a key value
        """
        if is_dead:
            return KeyCode.from_dead(name)
        elif name[0] == '<' and name[-1] == '>':
            return Key[name[1:-1]]
        else:
            return name

    def down(self, name, is_dead=False):
        """Triggers a key down event.

        :param str name: The name of the key. This is passed to
            :meth:`keycode`.

        :param bool is_dead: Whether a dead key press is requested. In that
            case, ``name`` must be a unicode character with a corresponding
            combining codepoint, and the key will be combined with the next
            character typed.
        """
        self.d.press(self.keycode(name, is_dead))

    def up(self, name, is_dead=False):
        """Triggers a key up event.

        :param str name: The name of the key. This is passed to
            :meth:`keycode`.

        :param bool is_dead: Whether a dead key press is requested. In that
            case, ``name`` must be a unicode character with a corresponding
            combining codepoint, and the key will be combined with the next
            character typed.
        """
        self.d.release(self.keycode(name, is_dead))
