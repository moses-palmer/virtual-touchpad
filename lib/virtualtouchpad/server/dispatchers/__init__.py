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


def _names(files):
    """Returns a list of module names based on a file listing.

    Only files ending with ``'.py'`` or ``'.pyc'``, and not beginning with
    ``'_'``, are included.

    :param [str] files: The files from which to generate a list of module names.

    :return: a list of unique module names
    """
    return list(set(file_name.rsplit('.', 1)[0]
        for file_name in files
        if file_name[0] != '_' and (
            file_name.endswith('.py') or file_name.endswith('.pyc'))))


import os
import pkg_resources
from virtualtouchpad import __name__ as PKG_RESOURCES_PACKAGE
__all__ = _names(pkg_resources.resource_listdir(
    PKG_RESOURCES_PACKAGE,
    os.path.join('server', 'dispatchers')))
