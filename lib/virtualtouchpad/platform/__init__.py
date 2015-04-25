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

import os
import pkg_resources

from contextlib import contextmanager


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
    candidate = '_' + ''.join(c for c in sys.platform if c.isalpha())
    driver = None
    try:
        driver = importlib.import_module(
            '.%s' % candidate,
            globals_dict['__package__'])
    except ImportError:
        driver = None
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


def _freeze_modules(target, *names):
    """Freezes imported modules for a target module.

    This function must be called before monkey-patching with gevent.

    This replaces every named imported module in the target module with an
    object that has all attributes that the module has, and the values at the
    time this function is called.

    :param target: The target module.

    :param [str] names: The names of the modules to freeze.
    """
    for name in names:
        class container(object):
            def __init__(self, source):
                for key in dir(source):
                    setattr(self, key, getattr(source, key))
        setattr(target, name, container(getattr(target, name)))
