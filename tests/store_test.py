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

from virtualtouchpad.configuration.notifier import Notifier
from virtualtouchpad.configuration import Store, Value


class StoreTest(unittest.TestCase):
    #: A sequence of items
    ITEM_LIST = (
        'value.one',
        'value.two',
        'another.value',
        'flat',
        'deeply.nested.collection.of.values.for.tests')

    #: A map of items and values
    VALUE_MAP = {
        'value': {
            'one': True,
            'two': True
        },
        'another': {
            'value': True
        },
        'flat': True,
        'deeply': {
            'nested': {
                'collection': {
                    'of': {
                        'values': {
                            'for': {
                                'tests': True
                            }
                        }
                    }
                }
            }
        }
    }

    def _notifier(self, item, value):
        try:
            self.__notifier(item, value)
        except AttributeError:
            pass

    @contextlib.contextmanager
    def notify(self, notifier):
        """Temporarily sets the status notifier.

        :param callable notifier: The temporary status callback.
        """
        self.__notifier = notifier
        try:
            yield
        finally:
            del self.__notifier


    def setUp(self):
        self.store = Store(self._notifier)

    def test_items_empty(self):
        """Tests that an empty status yields an empty value list"""
        self.assertSequenceEqual(
            [],
            self.store.items,
            str)

    def test_items(self):
        """Tests that a non-empty status yields the expected value list"""
        for name in self.ITEM_LIST:
            self.store.set(name, True)

        self.assertSequenceEqual(
            sorted(self.ITEM_LIST),
            sorted(self.store.items),
            str)

    def test_clear_makes_empty(self):
        """Tests that clearing a status causes the status to be empty"""
        for name in self.ITEM_LIST:
            self.store.set(name, True)

        self.store.clear()

        self.assertSequenceEqual(
            [],
            self.store.items,
            str)

    def test_clear_calls_callback(self):
        """Tests that clearing a status calls the callback"""
        for name in self.ITEM_LIST:
            self.store.set(name, True)

        values = []
        with self.notify(lambda item, value:
                values.append(item) or self.assertIsNone(value)):
            self.store.clear()

        self.assertSequenceEqual(
            sorted(values),
            sorted(self.ITEM_LIST),
            str)

    def test_get_non_existing(self):
        """Tests that get for non-existing value returns None"""
        self.assertIsNone(
            self.store.get('__i.do.not.exist__'))

    def test_get_existing(self):
        """Tests that get for non-existing value returns None"""
        expected = 'indeed'
        self.store.set('i.do.exist', expected)

        self.assertEqual(
            expected,
            self.store.get('i.do.exist'))
        self.assertIsNone(
            self.store.get('__i.do.not.exist__'))

    def test_get_invalid(self):
        """Tests that get for path that includes non-dict raises ValueError"""
        self.store.set('i.do.exist', True)

        with self.assertRaises(ValueError):
            self.store.get('i.do.exist.do.i.not?')

    def test_set_non_serializable(self):
        """Tests that setting a non-JSON serializable value raises TypeError"""
        with self.assertRaises(TypeError):
            self.store.set('i.cannot.be.set', object())

    def test_set_callback_new(self):
        """Tests that set calls the callback for new values"""
        values = []
        with self.notify(lambda item, value: values.append(item)):
            for name in self.ITEM_LIST:
                self.store.set(name, True)

        self.assertSequenceEqual(
            sorted(self.ITEM_LIST),
            sorted(self.store.items),
            str)

    def test_set_callback_modified(self):
        """Tests that set calls callback to be for new values"""
        for name in self.ITEM_LIST:
            self.store.set(name, True)

        values = []
        with self.notify(lambda item, value: values.append(item)):
            for name in self.ITEM_LIST:
                self.store.set(name, False)

        self.assertSequenceEqual(
            sorted(self.ITEM_LIST),
            sorted(self.store.items),
            str)

    def test_set_callback_not_modified(self):
        """Tests that set does not call callback for non-modified values"""
        for name in self.ITEM_LIST:
            self.store.set(name, True)

        values = []
        with self.notify(lambda item, value: values.append(item)):
            for name in self.ITEM_LIST:
                self.store.set(name, True)

        self.assertSequenceEqual(
            [],
            values,
            str)

    def test_select_empty(self):
        """Tests that select for an empty status returns an empty dict"""
        self.assertEqual(
            {},
            self.store.select(*self.ITEM_LIST))

    def test_select_non_empty(self):
        """Tests that select for a non-empty status returns a corresponding
        dict"""
        for name in self.ITEM_LIST:
            self.store.set(name, True)

        self.assertEqual(
            self.VALUE_MAP,
            self.store.select(*self.ITEM_LIST))

    def test_select_invalid(self):
        """Tests that select for a non-empty status returns a corresponding
        dict"""
        for name in self.ITEM_LIST:
            self.store.set(name, True)

        with self.assertRaises(ValueError):
            self.store.select(self.ITEM_LIST[0] + '.and.some.sub.elements')

    def test_update_values(self):
        """Tests that update correctly sets all values"""
        self.store.update(self.VALUE_MAP)

        for item in self.ITEM_LIST:
            self.assertTrue(
                self.store.get(item))

    def test_update_callback_new(self):
        """Tests that update calls the callback for new values"""
        values = []
        with self.notify(lambda item, value: values.append(item)):
            self.store.update(self.VALUE_MAP)

        self.assertSequenceEqual(
            sorted(self.ITEM_LIST),
            sorted(values),
            str)

    def test_update_callback_modified(self):
        """Tests that update calls the callback for modified values"""
        for name in self.ITEM_LIST:
            self.store.set(name, False)

        values = []
        with self.notify(lambda item, value: values.append(item)):
            self.store.update(self.VALUE_MAP)

        self.assertSequenceEqual(
            sorted(self.ITEM_LIST),
            sorted(values),
            str)

    def test_update_callback_not_modified(self):
        """Tests that update calls the callback for modified values"""
        for name in self.ITEM_LIST:
            self.store.set(name, True)

        values = []
        with self.notify(lambda item, value: values.append(item)):
            self.store.update(self.VALUE_MAP)

        self.assertSequenceEqual(
            [],
            values,
            str)

    def test_create_simple(self):
        """Tests that a simple status object can be created"""
        class Configuration(Store):
            FIRST = Value('val.first', 'First')
            SECOND = Value('val.second', 'Second')

        status = Configuration(Notifier(), **{
            'val.first': 1,
            'val.second': 2})
        self.assertEqual(
            1,
            status.FIRST)
        self.assertEqual(
            2,
            status.SECOND)

    def test_create_with_default(self):
        """Tests that a status object with default values works"""
        class Configuration(Store):
            FIRST = Value('val.first', 'First', default=lambda v: 1)
            SECOND = Value('val.second', 'Second', default=lambda v: 2)

        status = Configuration(Notifier())
        self.assertEqual(
            1,
            status.FIRST)
        self.assertEqual(
            2,
            status.SECOND)

    def test_set_readonly(self):
        """Tests that setting a read-only status value fails"""
        class Configuration(Store):
            FIRST = Value('val.first', 'First', False)
            SECOND = Value('val.second', 'Second', True)

        status = Configuration(Notifier())
        with self.assertRaises(AttributeError):
            status.SECOND = 2

    def test_set(self):
        """Tests that setting a read-only status value fails"""
        class Configuration(Store):
            FIRST = Value('val.first', 'First', False)
            SECOND = Value('val.second', 'Second', True)

        status = Configuration(Notifier())
        status.FIRST = 1
        self.assertEqual(
            1,
            status.FIRST)

    def test_notify(self):
        """Tests that a status object with default values works"""
        class Configuration(Store):
            FIRST = Value('val.first', 'First', False)
            SECOND = Value('val.second', 'Second', True)

        was_called = False
        def on_notify(name, value):
            nonlocal was_called
            was_called = True
            self.assertEqual(
                Configuration.FIRST.name,
                name)
            self.assertEqual(
                1,
                value)

        status = Configuration(Notifier())
        with status.notifier.registered(on_notify):
            status.FIRST = 1
        self.assertTrue(was_called)

        with self.assertRaises(AttributeError):
            status.SECOND = 2

    def test_values(self):
        """Tests that the values are returned correctly"""
        class Configuration(Store):
            FIRST = Value('val.first', 'First', default=lambda store: 1)
            SECOND = Value('val.second', 'Second', default=lambda store: 2)

        self.assertEquals(
            [(Configuration.FIRST, 1), (Configuration.SECOND, 2)],
            list(Configuration(Notifier()).values))
