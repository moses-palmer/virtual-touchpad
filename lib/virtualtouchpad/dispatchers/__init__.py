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

import logging

log = logging.getLogger(__name__)


class Dispatcher(object):
    """A class used to dispatch events to event handlers.
    """
    def __init__(self, **handlers):
        """Creates a dispatcher for a collection of handlers.

        :param handlers: The handlers to register. These must be callable, and
            they will be registered as the key names.
        """
        self._handlers = handlers

    def __call__(self, command, data):
        """Dispatches a command.

        :param str command: The command to dispatch.

        :param dict data: The arguments.

        :raises KeyError: if ``command`` is an unknown handler
        """
        try:
            name, method = command.split('.', 1)
            handler = getattr(self._handlers[name], method)
        except ValueError:
            handler = self._handlers[command]

        try:
            return handler(**data)
        except Exception as e:
            log.exception(
                'Failed to handle %s(%s): %s' % (
                    command,
                    ', '.join('%s=%s' % i for i in data.items()),
                    str(e)))
