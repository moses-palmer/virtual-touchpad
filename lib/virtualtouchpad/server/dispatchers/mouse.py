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

from . import dispatcher

from virtualtouchpad import event


log = logging.getLogger(__name__)


@dispatcher
def mouse_down(button=1):
    """Triggers a a mouse press event.

    :param int button: The button index.
    """
    try:
        event.mouse_down(int(button))
    except Exception as e:
        try:
            detail = e.args[0] % e.args[1:]
        except:
            detail = str(e)
        log.error('Failed to press button %d: %s' % (
            button, detail))


@dispatcher
def mouse_up(button=1):
    """Triggers a a mouse release event.

    :param int button: The button index.
    """
    try:
        event.mouse_up(int(button))
    except Exception as e:
        try:
            detail = e.args[0] % e.args[1:]
        except:
            detail = str(e)
        log.error('Failed to release button %d: %s' % (
            button, detail))


@dispatcher
def mouse_scroll(dx=0, dy=0):
    """Triggers a mouse scroll event.

    :param int dx: The horisontal offset to scroll.

    :param int dy: The vertical offset to scroll.
    """
    try:
        event.mouse_scroll(int(dx), int(dy))
    except Exception as e:
        try:
            detail = e.args[0] % e.args[1:]
        except:
            detail = str(e)
        log.error('Failed to scroll (%d, %d): %s' % (
            int(dx), int(dy), detail))


@dispatcher
def mouse_move(dx=0, dy=0):
    """Triggers a mouse move event.

    :param int dx: The horisontal offset to move.

    :param int dy: The vertical offset to move.
    """
    try:
        event.mouse_move(int(dx), int(dy))
    except Exception as e:
        try:
            detail = e.args[0] % e.args[1:]
        except:
            detail = str(e)
        log.error('Failed to move (%d, %d): %s' % (
            int(dx), int(dy), detail))
