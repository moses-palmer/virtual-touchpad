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

import pkg_resources
import os
import sys

import virtualtouchpad


#: The pkg_resources package name
PKG_RESOURCES_PACKAGE = virtualtouchpad.__name__

#: The name of the environment variable specifying a resource path override
STATIC_ROOT_ENV = 'VIRTUAL_TOUCHPAD_STATIC_ROOT'

#: The base directory for all files
RESOURCE_BASE = virtualtouchpad.__name__

#: The base directory for resources, relative to :attr:`RESOURCE_BASE`
RESOURCE_NAME = 'html'

#: The path, relative to some root directory, of the resources
RESOURCE_PATH = os.path.join(RESOURCE_BASE, RESOURCE_NAME)


def __get_static_root():
    def correct(path):
        result = os.path.realpath(path)
        return result if result[-1] == os.path.sep else result + os.path.sep

    # First use the environment variables
    try:
        root_from_env = os.environ[STATIC_ROOT_ENV]
        if os.path.isdir(root_from_env):
            return correct(root_from_env)

    except KeyError:
        # The environment variable is not set, ignore
        pass

    # Then handle frozen applications; expect them to put data alongside the
    # executable
    try:
        if sys.frozen:
            root_from_exe = os.path.join(
                os.path.dirname(sys.executable),
                RESOURCE_PATH)
            if os.path.isdir(root_from_exe):
                return correct(root_from_exe)

    except AttributeError:
        # The application is not frozen, ignore
        pass

    # If we can access the root directory of the package, fall back on that
    import virtualtouchpad
    root_from_package = os.path.join(
        os.path.dirname(virtualtouchpad.__file__),
        os.path.pardir,
        RESOURCE_PATH)
    if os.path.isdir(root_from_package):
        return correct(root_from_package)

    # If we have no root directory, we are probably running from an egg, and
    # we return None to make the functions below use pkg_resources
    return None


STATIC_ROOT = __get_static_root()


def _abs(path):
    """Translates a path to an absolute path.

    :param str path: The relative path.

    :return: an absolute path

    :raises FileNotFoundError: if the resulting path lies outside of the root; a
        successful return does not indicate that the file actually exists

    :raises ValueError: if no static root is set
    """
    if STATIC_ROOT is None:
        raise ValueError(STATIC_ROOT)

    if not path:
        return os.path.dirname(STATIC_ROOT)

    apath = os.path.realpath(os.path.join(STATIC_ROOT, path))
    if apath.startswith(STATIC_ROOT):
        return apath
    else:
        raise FileNotFoundError(path)


def exists(path):
    """Returns whether a static file exists.

    :param str path: The path of the static file.
    """
    try:
        return os.access(_abs(path), os.R_OK)

    except ValueError:
        return pkg_resources.resource_exists(
            PKG_RESOURCES_PACKAGE, os.path.join(RESOURCE_NAME, path))

    except:
        return False


def isdir(path):
    """Returns whether a static file exists and is a directory.

    :param str path: The path of the static file.
    """
    try:
        return os.path.isdir(_abs(path))

    except ValueError:
        return pkg_resources.resource_isdir(
            PKG_RESOURCES_PACKAGE, os.path.join(RESOURCE_NAME, path))

    except:
        return False


def list(path):
    """Lists all resources available under ``path``.

    :param str path: The path to check.

    :return: a list of resources
    :rtype: [str]
    """
    try:
        return os.listdir(_abs(path))

    except ValueError:
        return pkg_resources.resource_listdir(
            PKG_RESOURCES_PACKAGE,
            os.path.join(RESOURCE_NAME, path))

    except:
        return []


def open_stream(path):
    """Opens a file.

    :param str path: The path of the static file.

    :return: a file-like object
    """
    try:
        return open(_abs(path), 'rb')

    except ValueError:
        return pkg_resources.resource_stream(
            PKG_RESOURCES_PACKAGE,
            os.path.join(RESOURCE_NAME, path))

    except:
        raise FileNotFoundError(path)
