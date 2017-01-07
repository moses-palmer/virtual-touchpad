# coding=utf-8
# virtual-touchpad
# Copyright (C) 2013-2017 Moses Palmér
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

import contextlib
import enum
import unittest

from virtualtouchpad.status import Status


class StatusTest(unittest.TestCase):
    def status(self, configuration, **kwargs):
        return Status(configuration, **kwargs)

    def test_create_simple(self):
        """Tests that a simple status object can be created"""
        class Configuration(enum.Enum):
            FIRST = ('val.first', 'First')
            SECOND = ('val.second', 'Second')

        status = Status(Configuration, **{
            'val.first': 1,
            'val.second': 2})
        self.assertEqual(
            1,
            status.FIRST())
        self.assertEqual(
            2,
            status.SECOND())

    def test_create_with_default(self):
        """Tests that a status object with default values works"""
        class Configuration(enum.Enum):
            FIRST = ('val.first', 'First', True, lambda v: 1)
            SECOND = ('val.second', 'Second', True, lambda v: 2)

        status = Status(Configuration)
        self.assertEqual(
            1,
            status.FIRST())
        self.assertEqual(
            2,
            status.SECOND())

    def test_set_readonly(self):
        """Tests that setting a read-only status value fails"""
        class Configuration(enum.Enum):
            FIRST = ('val.first', 'First', False)
            SECOND = ('val.second', 'Second', True)

        status = Status(Configuration)
        with self.assertRaises(ValueError):
            status.SECOND.set(2)

    def test_set(self):
        """Tests that setting a read-only status value fails"""
        class Configuration(enum.Enum):
            FIRST = ('val.first', 'First', False)
            SECOND = ('val.second', 'Second', True)

        status = Status(Configuration)
        status.FIRST.set(1)
        self.assertEqual(
            1,
            status.FIRST())

    def test_notify(self):
        """Tests that a status object with default values works"""
        class Configuration(enum.Enum):
            FIRST = ('val.first', 'First', False)
            SECOND = ('val.second', 'Second', True)

        def on_notify(value):
            self.assertEqual(
                1,
                value)
            status.FIRST.was_called = True

        status = Status(Configuration)
        with status.FIRST.notify(on_notify):
            status.FIRST.set(1)
        self.assertTrue(hasattr(status.FIRST, 'was_called'))

        with self.assertRaises(ValueError):
            status.SECOND.set(2)
