#!/usr/bin/env python
# coding: utf8

import distutils
import distutils.command.build
import os
import setuptools

# Make sure we can import build
import sys
sys.path.append(os.path.join(
    os.path.dirname(__file__),
    'lib'))
import _build as buildlib


REQUIREMENTS = [
    'netifaces >=0.8',
    'Pillow >=1.1.7',
    'pynput >=1.0.5',
    'pystray >=0.3.3',
    'zeroconf >=0.17']

BUILD_REQUIREMENTS = [
    'cssmin',
    'polib >=1.0.4',
    'slimit']

#: Packages requires for different environments
EXTRA_PACKAGES = {
    ':python_version <= "2.7"': [
        'bottle >=0.11',
        'gevent >=0.13',
        'gevent-websocket >=0.9'],
    ':python_version >= "3.3"': [
        'aiohttp >=0.21']}

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
    extras_require=EXTRA_PACKAGES,

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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4'])


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
        ('generate_webapp_icons', None),
        ('generate_favicon', None)]


@build_command
class generate_webapp_icons(Command):
    description = 'generate web application icons from SVG sources'

    # The icon dimensions to generate
    DIMENSIONS = (196, 144, 114, 96, 72, 57, 48)

    def run(self):
        # Generate the application icons
        for size in self.DIMENSIONS:
            buildlib.icons.app_icon(
                size,
                os.path.join(
                    buildlib.HTML_ROOT,
                    'img',
                    'icon%dx%d.png' % (size, size)))


@build_command
class generate_favicon(Command):
    description = 'generate a favicon from SVG sources'

    # The icon dimensions to generate
    DIMENSIONS = (128, 64, 32, 16)

    def run(self):
        target_dir = os.path.join(
            os.path.dirname(__file__),
            'build',
            'icos')
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)

        # Generate the application icons
        for size in self.DIMENSIONS:
            buildlib.icons.app_icon(
                size,
                os.path.join(
                    target_dir,
                    'icon%dx%d.ico' % (size, size)))
        # Create the composite icon
        buildlib.icons.combine(
            os.path.join(
                    buildlib.HTML_ROOT,
                    'favicon.ico'),
            *(os.path.join(
                    target_dir,
                    'icon%dx%d.ico' % (size, size))
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
    setuptools.setup(**setup_arguments)
