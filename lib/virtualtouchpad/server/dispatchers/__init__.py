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
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.


#: A mapping from dispatcher name to dispatcher callback.
#:
#: This dict is populated by the @dispatcher decorator; do not modify it
#: directly.
_DISPATCHERS = {}


def dispatcher(f):
    """Marks a function as a dispatcher for *WebSocket* commands.

    :param f:
        The function to use as a *WebSocket* command dispatcher. Any websocket
        message, *JSON* decoded, where the ``command`` key value is equal to the
        name of this function will be handled by this function. It will be
        passed the ``data`` key value parameter expanded as parameters.
    """
    global _DISPATCHERS
    _DISPATCHERS[f.__name__] = f
    return f


def dispatch(command):
    """Dispatches a *WebSocket* command.

    :param dict command: The command to dispatch.

    :raises KeyError: if the ``command`` key is not a known dispatcher

    :raises ValueError: if either ``command`` or ``data`` is missing from
        ``command``
    """
    global _DISPATCHERS

    try:
        command_name = command['command']
        command_data = command['data']
    except KeyError:
        raise ValueError(command)

    return _DISPATCHERS[command_name](**command_data)


from . import keyboard, mouse
