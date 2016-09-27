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

import buildlib.commands.minify as minify


# Make sure we can import the main package
sys.path.append(LIBDIR)


REQUIREMENTS = [
    'aiohttp >=0.21',
    'netifaces >=0.8',
    'Pillow >=1.1.7',
    'pynput >=1.1.3',
    'pystray >=0.10',
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
        'html/*.*',
        'html/css/*.*',
        'html/help/*.*',
        'html/img/*.*',
        'html/js/*.*',
        'html/js/*/*.*',
        'html/keyboard/*.*',
        'html/keyboard/*/*.*',
        'html/translations/*/*.*']}


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


@build_command('generates raster icons')
class generate_raster_icons(Command):
    BASE = 'icon%dx%d.png'

    DIR = os.path.abspath(os.path.join(
        BUILDDIR, 'icons'))

    TARGET = os.path.join(DIR, BASE)

    # The icon dimensions to generate
    DIMENSIONS = (
        1024, 512, 256, 196, 144, 128, 114, 96, 72, 64, 57, 48, 32, 16)

    def run(self):
        if not os.path.isdir(self.DIR):
            os.makedirs(self.DIR)

        source_path = buildlib.icons.APP_ICON
        source_stat = os.stat(source_path)

        # Generate icons only for modified files
        for size in self.DIMENSIONS:
            target_path = self.TARGET % (size, size)
            try:
                target_stat = os.stat(target_path)
                if not (source_stat.st_mtime > target_stat.st_mtime):
                    continue
            except:
                pass
            buildlib.icons.convert(source_path, target_path, (size, size))


@build_command('generate a favicon from SVG sources',
               generate_raster_icons)
class generate_favicon(Command):
    BASE_ICO = 'favicon.ico'
    BASE_PNG = 'favicon.png'

    DIR = os.path.abspath(os.path.join(
        buildlib.HTML_ROOT))

    TARGET_ICO = os.path.join(DIR, BASE_ICO)
    TARGET_PNG = os.path.join(DIR, BASE_PNG)

    DIMENSIONS = (128, 64, 32, 16)

    def run(self):
        Command.run(self)
        buildlib.icons.combine(
            self.TARGET_ICO,
            *(
                generate_raster_icons.TARGET % (size, size)
                for size in self.DIMENSIONS))
        shutil.copy2(
            generate_raster_icons.TARGET % (
                self.DIMENSIONS[0], self.DIMENSIONS[0]),
            self.TARGET_PNG)


@build_command('generate the app icon for OSX',
               generate_raster_icons)
class generate_appicon_darwin(Command):
    BASE = 'icon-darwin.icns'

    DIR = generate_raster_icons.DIR

    TARGET = os.path.join(DIR, BASE)

    # The format used to generate the icon file names for the icon set; these
    # must match the files names for an OSX iconset directory
    BASE1X = 'icon_%dx%d.png'
    BASE2X = 'icon_%dx%d@2x.png'

    DIMENSIONS = (16, 32, 64, 128, 256, 512, 1024)

    @contextlib.contextmanager
    def _iconset(self):
        """Generates a temporary directory for the target *ICNS* iconset.

        The target directory exists only as long as this context manager is
        active.
        """
        tmpdir = tempfile.mkdtemp(suffix='.iconset')
        try:
            for size in self.DIMENSIONS:
                source_path = os.path.join(
                    generate_raster_icons.TARGET % (size, size))
                target_path1x = os.path.join(
                    tmpdir,
                    self.BASE1X % (size, size))
                target_path2x = os.path.join(
                    tmpdir,
                    self.BASE2X % (size // 2, size // 2))
                shutil.copy2(source_path, target_path1x)
                shutil.copy2(source_path, target_path2x)

            yield tmpdir

        finally:
            shutil.rmtree(tmpdir)

    def run(self):
        Command.run(self)
        try:
            with self._iconset() as tmpdir:
                subprocess.check_call([
                    'iconutil',
                    '--convert', 'icns',
                    tmpdir,
                    '--output', self.TARGET])
        except:
            if sys.platform == 'darwin':
                raise


@build_command('generate the app icon for Linux',
               generate_raster_icons)
class generate_appicon_linux(Command):
    BASE = 'icon-linux.png'

    DIR = generate_raster_icons.DIR

    TARGET = os.path.join(DIR, BASE)

    # The icon dimension to use
    DIMENSION = 128

    def run(self):
        Command.run(self)
        shutil.copy2(
            os.path.join(
                generate_raster_icons.TARGET % (
                    self.DIMENSION, self.DIMENSION)),
            self.TARGET)


@build_command('generate the app icon for Windows',
               generate_raster_icons)
class generate_appicon_win(Command):
    BASE = 'icon-win.ico'

    DIR = generate_raster_icons.DIR

    TARGET = os.path.join(DIR, BASE)

    # The icon dimensions to include
    DIMENSIONS = (128, 64, 32, 16)

    def run(self):
        Command.run(self)
        buildlib.icons.combine(
            self.TARGET,
            *(os.path.join(
                    generate_raster_icons.TARGET % (size, size))
                for size in self.DIMENSIONS))


@build_command('generate the app icon for all platforms',
               generate_appicon_darwin,
               generate_appicon_linux,
               generate_appicon_win)
class generate_appicon(Command):
    BASE = 'icon%dx%d.png'

    DIR = os.path.abspath(os.path.join(
        buildlib.HTML_ROOT, 'img'))

    TARGET = os.path.join(DIR, BASE)

    DIMENSIONS = (196, 144, 114, 72, 57)

    def run(self):
        Command.run(self)

        for size in self.DIMENSIONS:
            source_path = generate_raster_icons.TARGET % (size, size)
            target_path = self.TARGET % (size, size)
            shutil.copy2(source_path, target_path)


@build_command('generates all icons',
               generate_favicon,
               generate_appicon)
class generate_icons(Command):
    pass


@build_command('generate translation catalogues from PO files')
class generate_translations(Command):
    def run(self):
        import json

        source_dir = os.path.join(
            ROOT,
            'po')
        target_dir = os.path.join(
            buildlib.HTML_ROOT,
            'translations')

        for domain in os.listdir(source_dir):
            domain_path = os.path.join(source_dir, domain)
            if not os.path.isdir(domain_path):
                continue

            for language in os.listdir(domain_path):
                language_path = os.path.join(domain_path, language)
                if not language_path.endswith('.po'):
                    continue

                code, catalog = self.generate_catalog(language_path)
                with open(os.path.join(
                        target_dir,
                        domain,
                        code + '.js'), 'w') as f:
                    f.write('exports.translation.catalog=')
                    json.dump(catalog, f)

    def generate_catalog(self, language_path):
        import polib

        # Load the PO file
        pofile = polib.pofile(language_path)

        # Extract interesting meta data
        code = pofile.metadata['Language']
        plurals = {
            key.strip(): value.strip()
            for (key, value) in (
                keyvalue.split('=', 1)
                for keyvalue in pofile.metadata[
                    'Plural-Forms'].split(';')
                if keyvalue)}

        # Create the catalogue skeleton
        texts = {}
        catalog = {}
        catalog['code'] = code
        catalog['plural'] = plurals['plural']
        catalog['texts'] = texts

        # Populate the catalogue from the PO file
        for entry in pofile:
            texts[entry.msgid] = self.create_entry(entry, plurals)

        return code, catalog

    def create_entry(self, entry, plurals):
        # If this is a plural string, we first create a list of empty strings
        # and then populate it, otherwise we simply return the string
        if entry.msgid_plural:
            result = [''] * int(plurals['nplurals'])
            for n, msgstr in entry.msgstr_plural.items():
                result[int(n)] = msgstr
            return result

        else:
            return entry.msgstr


@build_command('update the POT files')
class xgettext(Command):
    def run(self):
        source_dir = buildlib.HTML_ROOT
        target_dir = os.path.join(
            ROOT,
            'po')

        for path in os.listdir(source_dir):
            # Only handle XHTML files
            if not path.endswith('.xhtml'):
                continue

            # Extract the text domain, and ignore minified files
            domain = path.rsplit('.', 1)[0]
            if domain.endswith('.min'):
                continue
            domain_path = os.path.join(target_dir, domain)

            potfile = os.path.join(target_dir, domain + '.pot')

            # Extract the messages and save the POT file
            full_path = os.path.join(source_dir, path)
            messages = buildlib.translation.read_translatable_strings(full_path)
            messages.save(potfile)

            # Make sure that the translation directory exists
            try:
                os.makedirs(domain_path)
            except OSError:
                pass

            # Update the old translations
            for f in os.listdir(domain_path):
                if not f.endswith('.po'):
                    continue

                pofile = os.path.join(target_dir, domain, f)

                buildlib.translation.merge_catalogs(potfile, pofile)


@build_command('install node dependencies')
class node_dependencies(Command):
    PACKAGE_COMMAND = ['npm', 'install']

    def node(self):
        """Makes sure that node.js is installed"""
        sys.stdout.write('Checking node.js installation...\n')

        # Since node.js picked an already used binary name, we must check
        # whether "node" is node.js or node - Amateur Packet Radio Node program;
        # The former actually provides output for the --version command
        try:
            node_output = subprocess.check_output(['node', '--version']).decode(
                'utf8')
            if node_output.strip():
                sys.stdout.write(node_output)
                return
        except OSError:
            pass

        # On Debian, node is called nodejs because of the above mentioned clash
        try:
            subprocess.check_call(['nodejs', '--version'])
            return
        except OSError:
            pass

        sys.stderr.write('node.js is not installed; terminating\n')
        sys.exit(1)

    def npm(self):
        """Makes sure that npm is installed"""
        sys.stdout.write('Checking npm installation...\n')

        try:
            subprocess.call(['npm', '--version'])
        except OSError:
            sys.stderr.write('npm is not installed; terminating\n')
            sys.exit(1)

    def packages(self):
        """Makes sure that dependencies are installed locally"""
        sys.stdout.write('Checking dependencies...\n')

        # Try to install it
        try:
            subprocess.check_call(self.PACKAGE_COMMAND)
            return
        except (OSError, subprocess.CalledProcessError):
            sys.stderr.write('Failed to install dependencies; terminating\n')
            sys.exit(1)

    def run(self):
        self.node()
        self.npm()
        self.packages()


@build_command('run tests',
               node_dependencies)
class test(setuptools.command.test.test):
    def run(self):
        Command.run(self)
        setuptools.command.test.test.run(self)


@build_command('generate all resources',
               minify.minify_html,
               generate_icons,
               generate_translations)
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
