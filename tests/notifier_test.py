# coding=utf-8
# virtual-touchpad
# Copyright (C) 2013-2016 Moses Palmér
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

import unittest

from virtualtouchpad import notifier


class NotifierTest(unittest.TestCase):
    def setUp(self):
        self.notifier = notifier.Notifier()

    def test_call(self):
        """Tests that a Notifier instance is callable"""
        self.notifier(1, 2, 3)

    def test_add_non_callable(self):
        """Tests that a non-callable object cannot be added to a Notifier"""
        with self.assertRaises(TypeError):
            self.notifier += 5

    def test_add_callable(self):
        """Tests that a callable object can be added to a notifier"""
        self.notifier += lambda: None

    def test_call_first(self):
        """Tests that calling a notifier calls the first callback registered"""
        class inner(object):
            def __init__(self, initial):
                self.value = initial

            def __call__(self, increment):
                self.value += increment

        callback = inner(5)
        self.notifier += callback
        self.notifier(5)

        self.assertEqual(
            10,
            callback.value)

    def test_call_once(self):
        """Tests that a callback can only be registered once"""
        class inner(object):
            def __init__(self, initial):
                self.value = initial

            def __call__(self, increment):
                self.value += increment

        callback = inner(5)
        self.notifier += callback
        self.notifier += callback
        self.notifier(5)

        self.assertEqual(
            10,
            callback.value)

    def test_call_all(self):
        """Tests that calling a notifier calls all callbacks registered"""
        class inner(object):
            def __init__(self, initial):
                self.value = initial

            def __call__(self, increment):
                self.value += increment

        callback1 = inner(5)
        self.notifier += callback1
        callback2 = inner(10)
        self.notifier += callback2
        self.notifier(5)

        self.assertEqual(
            10,
            callback1.value)
        self.assertEqual(
            15,
            callback2.value)

    def test_call_order(self):
        """Tests that calling a notifier calls all callbacks registered in the
        order they were registered"""
        class inner(object):
            def __init__(self):
                self.last_callback = 0

            def __getitem__(self, key):
                def test_inner(self):
                    assert self.last_callback + 1 == key, \
                        '%d was called out of order' % key
                    self.last_callback = key
                return inner

        callback = inner()
        self.notifier += callback[1]
        self.notifier += callback[2]
        self.notifier += callback[3]
        self.notifier += callback[4]
        self.notifier += callback[5]
        self.notifier()

    def test_sub_unregistered(self):
        """Tests that subtracting an non-registered callback raises
        ValueError"""
        with self.assertRaises(ValueError):
            self.notifier -= lambda: None

    def test_sub_registered(self):
        """Tests that a subtracted callback is not called"""
        class inner(object):
            def __init__(self, initial):
                self.value = initial

            def __call__(self, increment):
                self.value += increment

        callback = inner(5)
        self.notifier += callback
        self.notifier -= callback
        self.notifier(5)

        self.assertEqual(
            5,
            callback.value)

    def test_context_manager(self):
        """Tests that using a notifier as context manager works"""
        class inner(object):
            def __init__(self, initial):
                self.value = initial

            def __call__(self, increment):
                self.value += increment

        callback = inner(0)
        with self.notifier.registered(callback):
            for i in range(5):
                self.assertEqual(
                    i,
                    callback.value)
                self.notifier(1)
            self.notifier(1)
