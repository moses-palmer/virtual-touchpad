#!/usr/bin/env python
# coding: utf8

import contextlib
import distutils
import distutils.command.build
import os
import setuptools
import setuptools.command.test
import shutil
import subprocess
import sys
import tempfile

from setuptools import setup

# Make sure we can import buildlib and tests
sys.path.append(os.path.dirname(__file__))
import buildlib

from buildlib.commands import build_command, CMDCLASS, Command
from buildlib import ROOT, BUILDDIR, LIBDIR, PDIR

import buildlib.commands.icons as icons
import buildlib.commands.minify as minify
import buildlib.commands.node as node
import buildlib.commands.translations as translations


# Make sure we can import the main package
sys.path.append(LIBDIR)


REQUIREMENTS = [
    'aiohttp >=1.2',
    'netifaces >=0.8',
    'Pillow >=1.1.7',
    'pynput >=1.1.3',
    'pystray >=0.11',
    'zeroconf >=0.17']

BUILD_REQUIREMENTS = [
    'cssmin',
    'docutils',
    'polib >=1.0.4',
    'PyInstaller >=3.2',
    'slimit']

# The directories in which the packages can be found
PACKAGE_DIR = {
    'virtualtouchpad': 'lib/virtualtouchpad'}

# Data for the package; this will not be evaluated until the build steps have
# completed
PACKAGE_DATA = {
    'virtualtouchpad': [
        './*.png',
        'html/*.*',
        'html/css/*.*',
        'html/help/*.*',
        'html/img/*.*',
        'html/js/*.*',
        'html/js/*/*.*',
        'keyboard/*.*',
        'keyboard/*/*.*',
        'translations/*/*.*']}


# These are the arguments passed to setuptools.setup; they are further modified
# below
setup_arguments = dict(
    cmdclass=CMDCLASS,
    name='virtual-touchpad',
    description='Turns your mobile or tablet into a touchpad and keyboard '
    'for your computer.',

    install_requires=REQUIREMENTS,
    setup_requires=REQUIREMENTS + BUILD_REQUIREMENTS,

    author_email='moses.palmer@gmail.com',

    url='https://github.com/moses-palmer/virtual-touchpad',

    packages=setuptools.find_packages(LIBDIR),
    package_dir=PACKAGE_DIR,
    package_data=PACKAGE_DATA,
    zip_safe=True,
    test_suite='tests',

    license='GPLv3',
    platforms=['linux', 'windows'],
    keywords='control mouse, control keyboard',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5'])


@build_command('run tests',
               node.node_dependencies)
class test(setuptools.command.test.test):
    def run(self):
        Command.run(self)
        setuptools.command.test.test.run(self)


@build_command('update the POT files',
               translations.xgettext_xhtml,
               translations.xgettext_py)
class xgettext(Command):
    pass


@build_command('generate all resources',
               minify.minify_html,
               icons.generate_icons,
               translations.generate_translations)
class generate_res(Command):
    pass


@build_command('build the project',
               generate_res,
               *distutils.command.build.build.sub_commands)
class build(distutils.command.build.build):
    pass


@build_command('generate executable',
               build)
class build_exe(Command):
    SPEC_DIR = os.path.join(os.path.dirname(__file__), 'pyi')

    def run(self):
        Command.run(self)
        env = dict(os.environ)
        env['PYTHONPATH'] = os.pathsep.join(sys.path)
        for spec in os.listdir(self.SPEC_DIR):
            if not spec.endswith('.spec'):
                continue
            subprocess.check_call([
                'python', '-m', 'PyInstaller',
                os.path.join(self.SPEC_DIR, spec)],
                env=env)


# Read globals from virtualtouchpad._info without loading it
INFO = {}
with open(os.path.join(
        PDIR,
        '_info.py'), 'rb') as f:
    data = f.read().decode('utf-8')
    code = compile(data, '_info.py', 'exec')
    exec(code, {}, INFO)
setup_arguments['author'] = INFO['__author__']
setup_arguments['version'] = '.'.join(str(v) for v in INFO['__version__'])


# Read long description from several files
def read(name):
    try:
        with open(os.path.join(
                ROOT,
                name), 'rb') as f:
            return f.read().decode('utf-8')
    except IOError:
        return ''
setup_arguments['long_description'] = '\n\n'.join(
    read(name)
    for name in ('README.rst', 'CHANGES.rst'))


if __name__ == '__main__':
    setup(**setup_arguments)
