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
import pkg_resources
import os
import sys

from virtualtouchpad import __name__ as PKG_RESOURCES_PACKAGE


log = logging.getLogger(__name__)


def __get_static_root():
    # First use the environment variables
    try:
        root_from_env = os.environ['VIRTUAL_TOUCHPAD_STATIC_ROOT']
        if os.path.isdir(root_from_env):
            return root_from_env

    except KeyError:
        # The environment variable is not set, ignore
        pass

    # Then handle frozen applications; expect them to put data alongside the
    # executable
    try:
        if sys.frozen:
            root_from_exe = os.path.join(
                os.path.dirname(sys.executable),
                'virtualtouchpad', 'html')
            if os.path.isdir(root_from_exe):
                return root_from_exe

    except AttributeError:
        # The application is not frozen, ignore
        pass

    # If we can acces the root directory of the package, fall back on that
    import virtualtouchpad
    root_from_package = os.path.join(
        os.path.dirname(virtualtouchpad.__file__),
        'html')
    if os.path.isdir(root_from_package):
        return root_from_package


STATIC_ROOT = __get_static_root()


def exists(path):
    """Returns whether a static file exists.

    :param str path: The path of the static file.
    """
    if STATIC_ROOT is not None:
        return os.access(os.path.join(STATIC_ROOT, path), os.R_OK)

    else:
        return pkg_resources.resource_exists(
            PKG_RESOURCES_PACKAGE, os.path.join('html', path))


def isdir(path):
    """Returns whether a static file exists and is a directory.

    :param str path: The path of the static file.
    """
    if STATIC_ROOT is not None:
        return os.path.isdir(os.path.join(STATIC_ROOT, path))

    else:
        return pkg_resources.resource_isdir(
            PKG_RESOURCES_PACKAGE, os.path.join('html', path))


def list(path):
    """Lists all resources available under ``path``.

    :param str path: The path to check.

    :return: a list of resources
    :rtype: [str]
    """
    if STATIC_ROOT is not None:
        return os.listdir(os.path.join(STATIC_ROOT, path))

    else:
        return pkg_resources.resource_listdir(
            PKG_RESOURCES_PACKAGE,
            os.path.join('html', path))


def open_stream(path):
    """Opens a file.

    :param str path: The path of the static file.

    :return: a file-like object
    """
    if STATIC_ROOT is not None:
        return open(os.path.join(STATIC_ROOT, path), 'rb')

    else:
        return pkg_resources.resource_stream(
            PKG_RESOURCES_PACKAGE,
            os.path.join('html', path))
