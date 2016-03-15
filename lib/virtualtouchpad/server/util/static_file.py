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


# Set a default value for STATIC_ROOT only if it is accessible
DEFAULT_STATIC_ROOT = os.path.join(
    os.path.dirname(__file__),
    os.path.pardir,
    'html')
STATIC_ROOT = os.getenv(
    'VIRTUAL_TOUCHPAD_STATIC_ROOT',
    DEFAULT_STATIC_ROOT if os.access(DEFAULT_STATIC_ROOT, os.R_OK)
    else None)


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
        return open(os.path.join(STATIC_ROOT, path))

    else:
        return pkg_resources.resource_stream(
            PKG_RESOURCES_PACKAGE,
            os.path.join('html', path))
