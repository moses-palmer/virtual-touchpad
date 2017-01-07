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
import unittest

from virtualtouchpad.notifier import Notifier as _Notifier
from virtualtouchpad.store import Store as _Store
from virtualtouchpad.value import Value as _Value


class ValueTest(unittest.TestCase):
    def setUp(self):
        self.notifier = _Notifier()
        self.store = _Store(self.notifier)

        class Value(_Value):
            _notifier = self.notifier
            _store = self.store

        self.Value = Value

    def test_get_empty(self):
        """Tests that getting an undefined value returns None"""
        v = self.Value('test', '')
        self.assertIsNone(
            v())

    def test_get_default(self):
        """Tests that getting an undefined value returns None if default is
        set"""
        def default(value):
            self.assertEqual(
                v,
                value)
            return True

        v = self.Value('test', '', default=default)
        self.assertTrue(
            v())

    def test_get_initialized(self):
        """Tests that getting a value works"""
        v = self.Value('test', '')
        self.store.set(v.name, True)
        self.assertTrue(
            v())

    def test_set_readonly(self):
        """Tests that a read-only value cannot be set"""
        v = self.Value('test', '')
        with self.assertRaises(ValueError):
            v.set(True)

    def test_set(self):
        """Tests that setting a value works"""
        v = self.Value('test', '', readonly=False)
        v.set(True)
        self.assertTrue(
            v())

    def test_notify_store(self):
        """Tests that notify works when modifying store"""
        v = self.Value('test', '')

        def on_notify(value):
            self.assertTrue(value)
            v.was_called = True

        with v.notify(on_notify):
            self.store.set(v.name, True)

        self.assertTrue(
            hasattr(v, 'was_called'))

    def test_notify_set(self):
        """Tests that notify works when modifying value"""
        v = self.Value('test', '', readonly=False)

        def on_notify(value):
            self.assertTrue(value)
            v.was_called = True

        with v.notify(on_notify):
            v.set(True)

        self.assertTrue(
            hasattr(v, 'was_called'))
