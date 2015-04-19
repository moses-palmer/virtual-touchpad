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


import logging
log = logging.getLogger(__name__)

from ..dispatch import dispatcher

from .. import event


@dispatcher
def key_down(key):
    """Triggers a key down event.

    :param str key: The key that is being pressed. This value will be passed
        directly to :func:`event.key_down`.
    """
    try:
        event.key_down(key)
    except Exception as e:
        try:
            detail = e.args[0] % e.args[1:]
        except:
            detail = str(e)
        log.error('Failed to press key symbol %s: %s' % (key, detail))


@dispatcher
def key_up(key):
    """Triggers a key up event.

    :param str key: The key that is being release. This value will be passed
        directly to :func:`event.key_up`.
    """
    try:
        event.key_up(key)
    except Exception as e:
        try:
            detail = e.args[0] % e.args[1:]
        except:
            detail = str(e)
        log.error('Failed to release key symbol %s: %s' % (key, detail))
