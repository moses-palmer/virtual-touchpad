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
import os
import pkg_resources
import re

from contextlib import contextmanager


log = logging.getLogger(__name__)


class ImplementationImportError(Exception):
    """Raised when a module required for a platform specific implementation does
    not exist.
    """
    pass

@contextmanager
def modules():
    """A context manager for trying to import platform dependent modules.

    Use this in a ``with`` statement when importing platform dependent modules
    to allow :func:`implement` to gracefully try another implementation.
    """
    try:
        yield
    except ImportError as e:
        raise ImplementationImportError(e)


_package, _subpackage = __package__.split('.', 1)
_path = _subpackage.replace('.', os.path.sep)
__all__ = [directory
    for directory in pkg_resources.resource_listdir(_package, _path)
    if pkg_resources.resource_isdir(_package, os.path.join(_path, directory))
        and directory[0] != '_']


#: The regular expression used to match importable modules
_MODULE_RE = re.compile(r'[a-zA-Z][a-zA-Z0-9_]*\.pyc?$')


def _package_importables(package_name):
    """Yields all importable modules and packages in a package.

    Names beginning with ``'_'`` are ignored.

    :param str package_name: The name of the package.
    """
    package, subpackage = package_name.split('.', 1)
    path = subpackage.replace('.', os.path.sep)

    for name in pkg_resources.resource_listdir(package, path):
        if name[0] == '_':
            continue
        full = os.path.join(path, name)

        if not pkg_resources.resource_isdir(package, full):
            if _MODULE_RE.match(name):
                yield '.'.join((package_name, name.rsplit('.', 1)[0]))
        else:
            if any(pkg_resources.resource_exists(package,
                    os.path.join(full, f)) for f in (
                        '__init__.py',
                        '__init__.pyc')):
                yield '.'.join((package_name, name))


def implement(globals_dict):
    """Loads the platform dependent implementation and populates a dict.

    :param dict globals_dict: The globals dict. Use :func:`globals` when
        calling this function from another module. Only callable symbols not
        beginning with '_' in this dictionary will be imported from the driver
        module.

    :raises ImportError: if no platform driver was found, or a global callable
        in the driver was not present in ``globals_dict``, or the function
        signature of a global callable in the driver did not match in
        ``globals_dict``
    """
    import importlib
    import inspect
    import sys

    # Get the name of the platform and load the driver module
    package_name = globals_dict['__package__']
    driver = None
    for candidate in _package_importables(globals_dict['__package__']):
        try:
            driver = importlib.import_module(
                '.%s' % candidate.rsplit('.', 1)[-1],
                package_name)
        except ImplementationImportError as e:
            log.info('Not loading %s.%s: %s', package_name, candidate, str(e))

    if driver is None:
        raise ImportError('Failed to locate platform driver for package %s',
            globals_dict['__package__'])

    # Get symbols exported from the driver
    symbols = {}
    for name in dir(driver):
        value = getattr(driver, name)

        # We ignore all private symbols
        if name[0] == '_':
            continue

        # The symbol must exist as a global callable in this module
        old_value = globals_dict.get(name, None)
        if old_value is None:
            continue
        if not callable(old_value):
            raise ImportError(
                'error in %s: symbol <%s> must not be global',
                driver.__name__, name)

        # If the symbol is callable, we need a reference from which to retrieve
        # an argument specification
        if inspect.isclass(value):
            callable_value = value.__init__
            old_callable_value = old_value.__init__
        elif inspect.isfunction:
            callable_value = value
            old_callable_value = old_value
        else:
            callable_value = None
            old_callable_value = None

        # If the symbol is callable, the function signatures must match
        if callable(callable_value):
            argspec = inspect.getargspec(callable_value)
            old_argspec = inspect.getargspec(old_callable_value)
            if argspec != old_argspec:
                raise ImportError(
                    'error in %s: invalid method signature for <%s>',
                    driver.__name__, name)

        # Try to expand the documentation
        try:
            if value.__doc__:
                value.__doc__ +=  '\n\n' + old_value.__doc__
            else:
                value.__doc__ =  old_value.__doc__
        except AttributeError:
            pass

        # Replace the global
        globals_dict[name] = value
