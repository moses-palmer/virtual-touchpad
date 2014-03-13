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

import os

_root = os.path.dirname(__file__)
__all__ = [directory
    for directory in os.listdir(_root)
    if os.path.isdir(os.path.join(_root, directory)) and directory[0] != '_']


def _import_symbols(globals_dict, *candidates):
    """
    Loads the platform dependent implementation and populates a dict.

    @param globals_dict
        The globals dict. Use globals() when calling this function from another
        module. Only callable symbols not beginning with '_' in this dictionary
        will be imported from the driver module.
    @param candidates
        The names of candidate modules to try before trying the default platform
        driver. The default name is '_' + sys.platform, with everything but
        letters dripped from sys.platform.
    @raise ImportError if no platform driver was found, or a global callable in
        the driver was not present in globals_dict, or the function signature of
        a global callable in the driver did not match in globals_dict
    """
    import importlib
    import inspect
    import sys

    # Get the name of the platform and load the driver module
    platform_driver = '_' + ''.join(c for c in sys.platform if c.isalpha())
    driver = None
    for candidate in list(candidates) + [platform_driver]:
        try:
            driver = importlib.import_module(
                '.%s' % candidate,
                globals_dict['__package__'])
            break
        except ImportError:
            pass
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

        # If the symbol is callable, the function signatures must match
        if callable(value):
            argspec = inspect.getargspec(value)
            old_argspec = inspect.getargspec(old_value)
            if argspec != old_argspec:
                raise ImportError(
                    'error in %s: invalid method signature for <%s>',
                    driver.__name__, name)

        # Replace the global
        value.__doc__ = old_value.__doc__
        globals_dict[name] = value


def _freeze_modules(target, *names):
    """
    Freezes imported modules for a target module.

    This function must be called before monkey-patching with gevent.

    This replaces every named imported module in the target module with an
    object that has all attributes that the module has, and the values at the
    time this function is called.

    @param target
        The target module.
    @param names
        The names of the modules to freeze.
    """
    for name in names:
        class container(object):
            def __init__(self, source):
                for key in dir(source):
                    setattr(self, key, getattr(source, key))
        setattr(target, name, container(getattr(target, name)))
