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


def display_manager(display):
    """Traps *X* errors and raises a ``RuntimeError`` at the end if any error
    occurred.

    :param display: The *X* display.
    :type display: Xlib.display.Display

    :return: the display
    :rtype: Xlib.display.Display
    """
    from contextlib import contextmanager

    @contextmanager
    def manager():
        errors = []
        def handler(*args):
            errors.append(args)
        old_handler = display.set_error_handler(handler)
        yield display
        display.sync()
        display.set_error_handler(old_handler)
        if errors:
            log.error('X requests failed: %s', ', '.join(
                str(e) for e, v in errors))
            raise RuntimeError(errors)

    return manager()
