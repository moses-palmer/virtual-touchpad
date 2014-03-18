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

from . import _freeze_modules

# Make sure select is usable in Xlib
import Xlib.protocol.display
_freeze_modules(Xlib.protocol.display, 'select')

from Xlib import X
from Xlib import XK
from Xlib import display
from Xlib.ext.xtest import fake_input

try:
    import pyatspi
except ImportError:
    pyatspi = None

# The global X display
DISPLAY = display.Display()
