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

import enum

import virtualtouchpad._info as info

from .notifier import Notifier as _Notifier
from .store import Store as _Store
from .value import Value as _Value


class Configuration(enum.Enum):
    APPLICATION_VERSION = (
        'application.version',
        'The version of this application',
        True,
        lambda v: '.'.join(str(v) for v in info.__version__))
    SERVER_HOST = (
        'server.host',
        'The server hostname')
    SERVER_PORT = (
        'server.port',
        'The port of the server')
    SERVER_URL = (
        'server.url',
        'The URL of the server',
        True,
        lambda v: 'http://{}:{}/'.format(
            v.store.get(Configuration.SERVER_HOST.value[0]),
            v.store.get(Configuration.SERVER_PORT.value[0])))


class Status:
    def __init__(self, configuration, **kwargs):
        """Creates a new status instance.

        A ``Status`` instance holds a store, a notifier and a list of
        configuration values. Every configuration value is available as an
        instance of :class:`~virtualtouchpad.value.Value` under the name
        specified in the configuration.

        :param configuration: The configuration to use. This must be an
            :class:`~enum.Enum` instance with values compatible with the
            constructor arguments for :class:`~virtualtouchpad.value.Value`.

        :param kwargs: Any values to set on the status object before returning.
        """
        self._notifier = _Notifier()
        self._store = _Store(self._notifier)
        self._store.update(kwargs)

        class Value(_Value):
            _notifier = self._notifier
            _store = self._store

        self._values = []
        for v in configuration:
            self._values.append(Value(*v.value))
            setattr(self, v.name, self._values[-1])

    def __iter__(self):
        return iter(self._values)

    @property
    def store(self):
        """The backing store.
        """
        return self._store
