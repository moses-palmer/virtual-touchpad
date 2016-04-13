"""
Installs packages into the *virtualenv* container.

This is split into several parts:

*  Immediate invocation of *pip*. This is to install packages that cannot be
   reliably installed by *setuptools* from ``setup.py``.

*  Installation using ``setup.py develop``. This will install most of the
   dependencies.
"""

import distutils.sysconfig
import os
import subprocess
import sys

# Import setup.py in the root directory
sys.path.insert(0, '.')
import setup


VIRTUALENV = sys.prefix
PLATFORM = ''.join(c for c in sys.platform if c.isalpha())
PYTHON = sys.executable
SITE_PACKAGES = distutils.sysconfig.get_python_lib()


# Packages to install explicitly with pip before letting setuptools install
# dependencies; this set includes packages with native extensions, which are
# better installed as wheels to avoid having to compile them
EXPLICIT_PACKAGES = (
    'netifaces',
    'Pillow',
    'zeroconf')


def command(description, *args, **kwargs):
    """A thin wrapper around :class:`subprocess.Popen.communicate`.

    :param str description: A short description of the command. If the command
        exists normally, this is the only message that will be displayed.

    :param args: The command to execute.

    :param kwargs: Any keyword arguments passed to the constructor. The special
        value ``stdin_data`` is treated as data to send to the process.
    """
    stdin_data = kwargs.pop('stdin_data', b'')

    print(description)
    p = subprocess.Popen(
        list(args),
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        **kwargs)
    stdout, stderr = p.communicate(stdin_data)
    if p.returncode != 0:
        sys.stderr.write((stderr or stdout or b'<no output>\n').decode('utf-8'))
        raise subprocess.CalledProcessError(p.returncode, args, stdout + stderr)


def upgrade_core():
    """Ensures that *pip* and *setuptools* are upgraded.
    """
    command(
        'Upgrading core packages...',
        PYTHON, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools')


def install_explicit():
    """Installs all packages in ``EXPLICIT_PACKAGES`` with *pip*.

    This is necessary since packages installed with *setuptools* may not be
    installed as wheels.
    """
    command(
        'Installing %s...' % ', '.join(EXPLICIT_PACKAGES),
        PYTHON, '-m', 'pip', 'install', *EXPLICIT_PACKAGES)


def install_setup():
    """Installs all requirements by running ``setup.py``.
    """
    # TODO: Investigate why --install-dir is necessary on Windows; it appears
    # to work on Linux, but breaks on OSX
    command(
        'Installing dependencies...',
        PYTHON, 'setup.py', 'develop',
        *{
            'win': ['--install-dir=' + SITE_PACKAGES]}.get(PLATFORM, []))


upgrade_core()
install_explicit()
install_setup()
