"""
Imports packages from the system into a ``virtualenv`` container.

This takes care of two special cases:

*  The package is not installable by *pip*. This applies to for example
   *python-xorg* which does not have an installation candidate on *PyPi*.

*  Building the package takes a long time. This applies to the *Objective C*
   bindings on *OSX*.
"""

import distutils.sysconfig
import os
import subprocess
import sys

VIRTUALENV = sys.argv[1]
PLATFORM = ''.join(c for c in sys.platform if c.isalpha())
PYTHON = os.path.join(VIRTUALENV, {
    'darwin': 'bin',
    'linux': 'bin',
    'win': 'Scripts'}[PLATFORM], os.path.basename(sys.executable))
SITE_PACKAGES = subprocess.check_output([
    PYTHON, '-c',
    'from sys import stdout;'
    'from distutils.sysconfig import get_python_lib;'
    'stdout.write(get_python_lib())']).decode('utf-8')


PACKAGES = {
    'darwin': [],
    'linux': [
        'Xlib'],
    'win': []}[PLATFORM]


def import_package(name):
    """Imports a package from the system.

    :param str name: The name of the package to import.

    :return: whether the package was sucessfully imported
    """
    try:
        package = __import__(name)
        base = os.path.basename(os.path.dirname(package.__file__))
        target = os.path.join(SITE_PACKAGES, base)
        if not os.path.islink(target):
            os.symlink(
                os.path.dirname(package.__file__),
                target)
        return True

    except ImportError:
        return False


for package in PACKAGES:
    if import_package(package):
        print('"%s" sucessfully imported into virtualenv' % package)
    else:
        print('Failed to import "%s" into virtualenv;')
        sys.exit(1)
