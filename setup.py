#!/usr/bin/env python
# coding: utf8

import os
import setuptools

# Make sure we can import build
import sys
sys.path.append(os.path.join(
    os.path.dirname(__file__),
    'lib'))
import _build as buildlib


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


def build_helper(cls):
    """Registers a class as a helper command to run when invoking ``build``.

    :param cls: The command class.
    """
    import distutils.command.build

    distutils.command.build.build.sub_commands.append((cls.__name__, None))

    return build_command(cls)


@build_command
class xgettext(setuptools.Command):
    description = 'update the POT files'
    user_options = []

    def initialize_options(self): pass

    def finalize_options(self): pass

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


@build_helper
class minify_index(setuptools.Command):
    description = 'minify index.xhtml'
    user_options = []

    def initialize_options(self): pass

    def finalize_options(self): pass

    def run(self):
        # Load index.html
        dom_context = buildlib.xmltransform.start(
            os.path.join(
                buildlib.HTML_ROOT,
                'index.xhtml'))

        # Minify the index file
        buildlib.xmltransform.minify_html(dom_context)

        # Add the manifest file
        buildlib.xmltransform.add_manifest(
            dom_context,
            'virtual-touchpad.appcache')

        # Write index.min.xhtml
        buildlib.xmltransform.end(
            dom_context,
            os.path.join(
                buildlib.HTML_ROOT,
                'index.min.xhtml'))


@build_helper
class minify_help(setuptools.Command):
    description = 'minify help/index.xhtml'
    user_options = []

    def initialize_options(self): pass

    def finalize_options(self): pass

    def run(self):
        # Load help.xhtml
        dom_context = buildlib.xmltransform.start(
            os.path.join(
                buildlib.HTML_ROOT,
                'help',
                'index.xhtml'))

        # Minify the index file
        buildlib.xmltransform.minify_html(dom_context)

        # Write help.min.xhtml
        buildlib.xmltransform.end(
            dom_context,
            os.path.join(
                buildlib.HTML_ROOT,
                'help',
                'index.min.xhtml'))


@build_helper
class generate_webapp_icons(setuptools.Command):
    description = 'generate web application icons from SVG sources'
    user_options = []

    def initialize_options(self): pass

    def finalize_options(self): pass

    def run(self):
        # Generate the application icons
        for size in (196, 144, 114, 96, 72, 57, 48):
            buildlib.icons.app_icon(
                size,
                os.path.join(
                    buildlib.HTML_ROOT,
                    'img',
                    'icon%dx%d.png' % (size, size)))


@build_helper
class generate_favicon(setuptools.Command):
    description = 'generate a favicon from SVG sources'
    user_options = []
    DIMENSIONS = (128, 64, 32, 16)

    def initialize_options(self): pass

    def finalize_options(self): pass

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
        buildlib.icons.combine(
            os.path.join(
                    buildlib.HTML_ROOT,
                    'favicon.ico'),
            *(os.path.join(
                    target_dir,
                    'icon%dx%d.ico' % (size, size))
                for size in self.DIMENSIONS))


@build_helper
class generate_translations(setuptools.Command):
    description = 'generate translation catalogues from PO files'
    user_options = []

    def initialize_options(self): pass

    def finalize_options(self): pass

    def run(self):
        import json
        import polib

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
            # Only handle directories under the source directory
            domain_path = os.path.join(source_dir, domain)
            if not os.path.isdir(domain_path):
                continue

            for language in os.listdir(domain_path):
                # Load the PO file
                language_path = os.path.join(domain_path, language)
                if not language_path.endswith('.po'):
                    continue
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
                    if entry.msgid_plural:
                        # If this is a plural string, we first create a list of
                        # empty strings and then populate it
                        texts[entry.msgid] = [''] * int(
                            plurals['nplurals'])
                        for n, msgstr in entry.msgstr_plural.items():
                            texts[entry.msgid][int(n)] = msgstr

                    else:
                        # If this is non-plural string, we simply copy it
                        texts[entry.msgid] = entry.msgstr

                # Write the catalogue as JavaScript code
                with open(os.path.join(
                        target_dir,
                        domain,
                        code + '.js'), 'w') as f:
                    f.write('exports.translation.catalog=')
                    json.dump(catalog, f)


# Read globals from virtualtouchpad._info without loading it
INFO = {}
with open(os.path.join(
        os.path.dirname(__file__),
        'lib',
        'virtualtouchpad',
        '_info.py')) as f:
    for line in f:
        try:
            name, value = (i.strip() for i in line.split('='))
            if name.startswith('__') and name.endswith('__'):
                INFO[name[2:-2]] = eval(value)
        except ValueError:
            pass
setup_arguments['author'] = INFO['author']
setup_arguments['version'] = '.'.join(str(i) for i in INFO['version']),


# Read long description from several files
def read(name):
    try:
        with open(os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                name)) as f:
            return f.read()
    except IOError:
        return ''
setup_arguments['long_description'] = '\n\n'.join(
    read(name)
    for name in ('README.rst', 'CHANGES.rst'))


setuptools.setup(**setup_arguments)
