# coding=utf-8
'''
virtual-touchpad
Copyright (C) 2013-2014 Moses Palmér

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
'''

import ctypes

_SendInput = ctypes.windll.user32.SendInput


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


def key_down(key):
    global _SendInput
    raise NotImplementedError();


def key_up(key):
    global _SendInput
    raise NotImplementedError();


def mouse_down(button):
    global _SendInput

    _SendInput(1,
        ctypes.byref(INPUT(
            type = INPUT.MOUSE,
            value = ANYINPUT(
                mouse = MOUSEINPUT(
                    dwFlags = MOUSEINPUT.BUTTON_MAPPING[button][0])))),
        ctypes.sizeof(INPUT))


def mouse_up(button):
    global _SendInput

    _SendInput(1,
        ctypes.byref(INPUT(
            type = INPUT.MOUSE,
            value = ANYINPUT(
                mouse = MOUSEINPUT(
                    dwFlags = MOUSEINPUT.BUTTON_MAPPING[button][1])))),
        ctypes.sizeof(INPUT))


def mouse_scroll(dx, dy):
    global _SendInput

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
    global _SendInput

    _SendInput(1,
        ctypes.byref(INPUT(
            type = INPUT.MOUSE,
            value = ANYINPUT(
                mouse = MOUSEINPUT(
                    dx = int(dx),
                    dy = int(dy),
                    dwFlags = MOUSEINPUT.MOVE)))),
        ctypes.sizeof(INPUT))
