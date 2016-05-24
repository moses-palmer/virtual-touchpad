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

import contextlib
import types


class Value:
    _notifier = None
    _store = None

    def __init__(self, name, description, readonly=True, default=None):
        """A configuration value.

        :param str name: The name of the value on the form
            ``'section.sub.value'``.

        :param str description: A short description.

        :param bool readonly: Whether the value is read-only.

        :param callable default: A getter for the value if not specified. This
            will be called if the store returns ``None``, and will be passed the
            value as its only parameter.

        :return: a value
        """
        self._name = name
        self.__doc__ = description
        self._readonly = readonly
        self._getter = types.MethodType(default or (lambda self: None), self)

    @property
    def name(self):
        """The name of the store property.
        """
        return self._name

    @property
    def readonly(self):
        """Whether this value is read-only.
        """
        return self._readonly

    @property
    def store(self):
        """The store used by this class.
        """
        return self._store

    def __call__(self):
        """Reads the store value.
        """
        if self._store is None:
            return

        else:
            result = self._store.get(self.name)
            if result is None:
                return self._getter()
            else:
                return result

    def set(self, value):
        """Sets a new value.

        :param value: The new value.

        :raises ValueError: if the value is read-only
        """
        if self._readonly:
            raise ValueError(value)

        elif self._store is None:
            return

        else:
            self._store.set(self.name, value)

    @contextlib.contextmanager
    def notify(self, callback):
        """Registers a callback to be called when the store value changes.

        The callback will be called with the new value as its only parameter.
        """
        if self._notifier is None:
            yield

        else:
            def on_notify(item, value):
                if item == self.name:
                    callback(value)

            self._notifier += on_notify
            try:
                yield
            finally:
                self._notifier -= on_notify
