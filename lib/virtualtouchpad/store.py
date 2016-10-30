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

import json


class Store(object):
    def __init__(self, notifier):
        """A class to manage a key-value store.

        :param callable notifier: A callback to call whenever a value is changed
            by this class. It will be called with the arguments
            ``(name, new_value)``.
        """
        self._notifier = notifier
        self._data = {}

    def _canonical(self, value):
        """Retrieves a canonical representation for a value.

        This is performed by *JSON* serializing the value and then parsing it.

        :param value: The value to modify.

        :return: a canonical representation of ``value``

        :raises TypeError: if the value is not *JSON* serializable
        """
        return json.loads(json.dumps(value))

    def _set(self, target, item, value):
        """Sets a value.

        If the full path to the value does not exist, it is created,

        :param dict target: The target ``dict``.

        :param str item: The path to the value to set. This should be on
            the form ``some.path.to.value``.

        :return: whether the value was modified
        :rtype: bool

        :raises ValueError: if any value along the item path is set, but not a
            ``dict``
        """
        parts = item.split('.')

        # Iterate over all but the last item in the item path
        for part in parts[:-1]:
            # if value.get raises AttributeError, it is not a dict
            try:
                next_target = target.get(part, None)
            except AttributeError:
                raise ValueError(item)

            # If the item did not exist, create it and make sure to set it
            if next_target is None:
                next_target = {}
                target[part] = next_target

            target = next_target

        # Read the previous value, and make sure to reraise errors as ValueError
        try:
            previous_value = target.get(parts[-1], None)
        except AttributeError:
            raise ValueError(item)

        # Update the cache only if the value is different
        if value != previous_value:
            target[parts[-1]] = value
            return True
        else:
            return False

    @classmethod
    def extract_items(self, data):
        """Converts a dict to a sequence of item names.
        """
        def handle(collection, root, value):
            if isinstance(value, dict):
                for k, v in value.items():
                    handle(
                        collection,
                        '.'.join((root, k)) if root else k,
                        v)
            else:
                collection.add(root)
            return collection
        return handle(set(), None, data)

    @property
    def items(self):
        """The entire list of items.
        """
        return self.extract_items(self._data)

    def clear(self):
        """Clears the entire cache.

        This method will first call :meth:`set` for all current items with a
        value of ``None`` and then clear the cache.
        """
        for item in self.items:
            self.set(item, None)
        self._data = {}

    def get(self, item):
        """Retrieves a value, or ``None`` if it is not set.

        :param str item: The path to the value to retrieve. This should be on
            the form ``some.path.to.value``.

        :return: the value requested, or ``None``

        :raises ValueError: if any value along the item path is not a ``dict``
        """
        value = self._data

        # Iterate over all items in the item path
        for part in item.split('.'):
            # if value.get raises AttributeError, it is not a dict
            try:
                value = value.get(part, None)
            except AttributeError:
                raise ValueError(item)

            # Have we reached the end?
            if value is None:
                return value

        return value

    def set(self, item, value):
        """Sets a value.

        The value is *JSON* serialized and then parsed again to get a canonical
        value to set. If the value is different from the current value, the
        notifier is called with the arguments ``(item, canonical_value)``.

        If the full path to the value does not exist, it is created,

        :param str item: The path to the value to set. This should be on
            the form ``some.path.to.value``.

        :raises ValueError: if any value along the item path is set, but not a
            ``dict``

        :raises TypeError: if the value is not *JSON* serializable
        """
        value = self._canonical(value)
        if self._set(self._data, item, value):
            self._notifier(item, value)

    def select(self, *items):
        """Selects a set of items from the store and returns them as a ``dict``.

        Unset values are excluded.

        :param items: The items to retrieve.

        :raises ValueError: if any value along any item path is set, but not a
            ``dict``
        """
        result = {}

        for item in items:
            value = self.get(item)
            if not value is None:
                self._set(result, item, value)

        return result

    def update(self, value):
        """Updates multiple items.

        This method will recurse down ``value``, and for every value that is
        not a ``dict``, :meth:`set` will be called.

        :param dict value: The source value to use for updating.

        :raises ValueError: if any value along any item path is set, but not a
            ``dict``
        """
        def update(value, target):
            if isinstance(value, dict):
                for k, v in value.items():
                    update(
                        v,
                        '.'.join((target, k)) if target else k)
            elif target:
                self.set(target, value)
            else:
                raise ValueError()

        update(value, None)
