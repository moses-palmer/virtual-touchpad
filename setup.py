#!/usr/bin/env python
# coding: utf8

import contextlib
import distutils
import distutils.command.build
import os
import setuptools
import shutil
import subprocess
import tempfile

from setuptools import setup

# Make sure we can import build
import sys
sys.path.append(os.path.join(
    os.path.dirname(__file__),
    'lib'))
import _build as buildlib


REQUIREMENTS = [
    'aiohttp >=0.21',
    'netifaces >=0.8',
    'Pillow >=1.1.7',
    'pynput >=1.0.5',
    'pystray >=0.3.3',
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
        'html/img/*.*',
        'html/js/*.*',
        'html/js/*/*.*',
        'html/keyboard/*.*',
        'html/keyboard/*/*.*',
        'html/translations/*/*.*']}


# These are the arguments passed to setuptools.setup; they are further modified
# below
setup_arguments = dict(
    cmdclass={},
    name='virtual-touchpad',
    description='Turns your mobile or tablet into a touchpad and keyboard '
    'for your computer.',

    install_requires=REQUIREMENTS,
    setup_requires=REQUIREMENTS + BUILD_REQUIREMENTS,

    author_email='moses.palmer@gmail.com',

    url='https://github.com/moses-palmer/virtual-touchpad',

    packages=setuptools.find_packages(
        os.path.join(
            os.path.dirname(__file__),
            'lib'),
        exclude=[
            '_build']),
    package_dir=PACKAGE_DIR,
    package_data=PACKAGE_DATA,
    zip_safe=True,

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


def build_command(cls):
    """Registers a class as a build command.

    :param cls: The command class.
    """
    setup_arguments['cmdclass'][cls.__name__] = cls

    return cls


class Command(setuptools.Command):
    """Convenience class to avoid having to define all required fields.
    """
    user_options = []
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)


@build_command
class build(distutils.command.build.build):
    sub_commands = list(distutils.command.build.build.sub_commands) + [
        ('generate_res', None)]


@build_command
class generate_res(Command):
    description = 'generates all resources'
    sub_commands = [
        ('minify_html', None),
        ('generate_icons', None),
        ('generate_translations', None)]


@build_command
class minify_html(Command):
    files = (
        ('index.xhtml', True),
        ('help/index.xhtml', False))
    description = 'minify html files'

    def minify(self, name, include_appcache):
        dom_context = buildlib.xmltransform.start(
            os.path.join(
                buildlib.HTML_ROOT,
                name))

        buildlib.xmltransform.minify_html(dom_context)

        if include_appcache:
            buildlib.xmltransform.add_manifest(
                dom_context,
                'virtual-touchpad.appcache')

        base, ext = name.rsplit('.', 1)
        buildlib.xmltransform.end(
            dom_context,
            os.path.join(
                buildlib.HTML_ROOT,
                base + '.min.' + ext))

    def run(self):
        for name, include_appcache in self.files:
            self.minify(name, include_appcache)


@build_command
class generate_icons(Command):
    description = 'generates all icons'
    sub_commands = [
        ('generate_favicon', None),
        ('generate_appicon', None)]


@build_command
class generate_raster_icons(Command):
    description = 'generates raster icons'

    BASE = 'icon%dx%d.png'

    DIR = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'build', 'icons'))

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
                if not (source_stat.st_mtime > target_stat.st_mtime) :
                    continue
            except:
                pass
            buildlib.icons.convert(source_path, target_path, (size, size))


@build_command
class generate_favicon(Command):
    description = 'generate a favicon from SVG sources'
    sub_commands = [
        ('generate_raster_icons', None)]

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


@build_command
class generate_appicon(Command):
    description = 'generate the app icon for all platforms'
    sub_commands = [
        ('generate_raster_icons', None),
        ('generate_appicon_darwin', None),
        ('generate_appicon_linux', None),
        ('generate_appicon_win', None)]

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


@build_command
class generate_appicon_darwin(Command):
    description = 'generate the app icon for OSX'
    sub_commands = [
        ('generate_raster_icons', None)]

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


@build_command
class generate_appicon_linux(Command):
    description = 'generate the app icon for Linux'
    sub_commands = [
        ('generate_raster_icons', None)]

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


@build_command
class generate_appicon_win(Command):
    description = 'generate the app icon for Windows'
    sub_commands = [
        ('generate_raster_icons', None)]

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


@build_command
class generate_translations(Command):
    description = 'generate translation catalogues from PO files'

    def run(self):
        import json

        source_dir = os.path.join(
            os.path.dirname(__file__),
            'po')
        target_dir = os.path.join(
            os.path.dirname(__file__),
            'lib',
            'virtualtouchpad',
            'html',
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


@build_command
class xgettext(Command):
    description = 'update the POT files'

    def run(self):
        source_dir = buildlib.HTML_ROOT
        target_dir = os.path.join(
            os.path.dirname(__file__),
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


@build_command
class build_exe(Command):
    description = 'generate executable'
    sub_commands = list(distutils.command.build.build.sub_commands) + [
        ('build', None)]

    SPEC_DIR = os.path.join(os.path.dirname(__file__), 'pyi')

    def run(self):
        Command.run(self)
        env = dict(os.environ)
        env['PYTHONPATH'] = os.pathsep.join(sys.path)
        for spec in os.listdir(self.SPEC_DIR):
            subprocess.check_call([
                'python', '-m', 'PyInstaller',
                os.path.join(self.SPEC_DIR, spec)],
                env=env)


# Read globals from virtualtouchpad._info without loading it
INFO = {}
with open(os.path.join(
        os.path.dirname(__file__),
        'lib',
        'virtualtouchpad',
        '_info.py'), 'rb') as f:
    data = f.read().decode('utf-8') if sys.version_info.major >= 3 else f.read()
    code = compile(data, '_info.py', 'exec')
    exec(code, {}, INFO)
setup_arguments['author'] = INFO['__author__']
setup_arguments['version'] = '.'.join(str(v) for v in INFO['__version__'])


# Read long description from several files
def read(name):
    try:
        with open(os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                name), 'rb') as f:
            return f.read().decode('utf-8')
    except IOError:
        return ''
setup_arguments['long_description'] = '\n\n'.join(
    read(name)
    for name in ('README.rst', 'CHANGES.rst'))


if __name__ == '__main__':
    setup(**setup_arguments)
