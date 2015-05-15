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
import threading


class Notifier(object):
    """A class allowing to call a list of functions sequentially.

    Regardless of how many times a callback is registered, it will only be
    called once. Callbacks will be called in the order they are registered.
    """
    def __init__(self):
        """Creates a new ``Notifier``.
        """
        self._callbacks = []
        self._lock = threading.RLock()

    def __call__(self, *args, **kwargs):
        with self._lock:
            for callback in self._callbacks:
                callback(*args, **kwargs)

    def __add__(self, callback):
        if not callable(callback):
            raise TypeError('%s is not callable', str(callback))
        with self._lock:
            if not callback in self._callbacks:
                self._callbacks.append(callback)
            return self

    def __sub__(self, callback):
        with self._lock:
            index = self._callbacks.index(callback)
            del self._callbacks[index]
            return self

    @contextlib.contextmanager
    def registered(self, callback):
        """Runs a code block with a callback temporarily registered.

        :param callable callback: The callback.
        """
        self += callback
        try:
            yield
        finally:
            self -= callback
