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

from virtualtouchpad import platform
with platform.modules():
    import win32api

import ctypes
import logging
import unicodedata

from ._win32_syms import SYMS


log = logging.getLogger(__name__)


_SendInput = ctypes.windll.user32.SendInput

#: The last dead key; TODO: Set this per connection
dead_key = None


class MOUSEINPUT(ctypes.Structure):
    MOVE = 0x0001
    LEFTDOWN = 0x0002
    LEFTUP = 0x0004
    RIGHTDOWN = 0x0008
    RIGHTUP = 0x0010
    MIDDLEDOWN = 0x0020
    MIDDLEUP = 0x0040
    WHEEL = 0x0800

    BUTTON_MAPPING = {
        1: (LEFTDOWN, LEFTUP),
        2: (MIDDLEDOWN, MIDDLEUP),
        3: (RIGHTDOWN, RIGHTUP)}

    _fields_ = [
        ('dx', ctypes.c_int32),
        ('dy', ctypes.c_int32),
        ('mouseData', ctypes.c_uint32),
        ('dwFlags', ctypes.c_uint32),
        ('time', ctypes.c_uint32),
        ('dwExtraInfo', ctypes.c_void_p)]


class KEYBDINPUT(ctypes.Structure):
    EXTENDEDKEY = 0x0001
    KEYUP = 0x0002
    SCANCODE = 0x0008
    UNICODE = 0x0004

    _fields_ = [
        ('wVk', ctypes.c_uint16),
        ('wScan', ctypes.c_uint16),
        ('dwFlags', ctypes.c_uint32),
        ('time', ctypes.c_uint32),
        ('dwExtraInfo', ctypes.c_void_p)]

class ANYINPUT(ctypes.Union):
    _fields_ = [
        ('mouse', MOUSEINPUT),
        ('keyboard', KEYBDINPUT)]

class INPUT(ctypes.Structure):
    MOUSE = 0
    KEYBOARD = 1

    _fields_ = [
        ('type', ctypes.c_uint32),
        ('value', ANYINPUT)]


def is_dead(symbol):
    """Returns whether a key symbol is a dead key.

    :param symbol: The key symbol.
    :type symbol: str or None

    :return: whether ``symbol`` is a dead key
    """
    return symbol and symbol.startswith('dead_')


def set_dead_key(name):
    """Sets the current dead key.

    :param str name: The name of the key. This should be the actual character
        representing the dead key, such as ``~`` for *TILDE*.

    :raises KeyError: if the dead cannot be converted to a combining character
    """
    # TODO: Use a per connection store
    global dead_key

    if name is None:
        dead_key = None
    else:
        dead_key = (
            name,
            unicodedata.lookup('COMBINING ' + unicodedata.name(name)))


def key_event(name, symbol, flags):
    """Sends a keyboard event.

    If the length of ``name`` is ``1``, it is assumed to be a *unicode*
    character and the corresponding character will be sent.

    Otherwise, symbol is mapped
    """
    if name and len(name) == 1:
        keyboard = KEYBDINPUT(
            dwFlags = KEYBDINPUT.UNICODE | flags,
            wScan = ord(name))
    else:
        try:
            vk = SYMS[symbol]
        except KeyError:
            log.error('Unknown symbol: %s', symbol)
            return
        keyboard = KEYBDINPUT(
            dwFlags = flags,
            wVk = vk)
    _SendInput(1,
        ctypes.byref(INPUT(
            type = INPUT.KEYBOARD,
            value = ANYINPUT(
                keyboard = keyboard))),
        ctypes.sizeof(INPUT))


def key_down(name, keysym, symbol):
    # Do we have a previous dead key? In that case, first try to combine it with
    # the current key, and send it, and if that fails just send the dead key
    # alone
    global dead_key

    if not dead_key is None:
        previous_name, combining = dead_key
        set_dead_key(None)
        if name and len(name) == 1:
            combined = unicodedata.normalize('NFC', name + combining)
            if len(combined) == 1:
                key_event(combined, None, 0)
                return
        key_event(previous_name, None, 0)

    # If the current key is a dead key, save it for later
    if is_dead(symbol):
        try:
            set_dead_key(name)
            return
        except Exception as e:
            log.error('Failed to set dead key: %s', str(e))

    key_event(name, symbol, 0)


def key_up(name, keysym, symbol):
    key_event(name, symbol, KEYBDINPUT.KEYUP)


def mouse_down(button):
    _SendInput(1,
        ctypes.byref(INPUT(
            type = INPUT.MOUSE,
            value = ANYINPUT(
                mouse = MOUSEINPUT(
                    dwFlags = MOUSEINPUT.BUTTON_MAPPING[button][0])))),
        ctypes.sizeof(INPUT))


def mouse_up(button):
    _SendInput(1,
        ctypes.byref(INPUT(
            type = INPUT.MOUSE,
            value = ANYINPUT(
                mouse = MOUSEINPUT(
                    dwFlags = MOUSEINPUT.BUTTON_MAPPING[button][1])))),
        ctypes.sizeof(INPUT))


def mouse_scroll(dx, dy):
    # TODO: Support horisontal scroll
    _SendInput(1,
        ctypes.byref(INPUT(
            type = INPUT.MOUSE,
            value = ANYINPUT(
                mouse = MOUSEINPUT(
                    dwFlags = MOUSEINPUT.WHEEL,
                    mouseData = dy)))),
        ctypes.sizeof(INPUT))


def mouse_move(dx, dy):
    _SendInput(1,
        ctypes.byref(INPUT(
            type = INPUT.MOUSE,
            value = ANYINPUT(
                mouse = MOUSEINPUT(
                    dx = int(dx),
                    dy = int(dy),
                    dwFlags = MOUSEINPUT.MOVE)))),
        ctypes.sizeof(INPUT))
