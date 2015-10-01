#!/usr/bin/env python
# coding: utf8

import os
import setuptools

# Make sure we can import build
import sys
sys.path.append(os.path.join(
    os.path.dirname(__file__),
    'lib'))
sys.path.append(os.path.join(
    os.path.dirname(__file__),
    'lib-setup'))
import build

try:
    import py2exe
except ImportError:
    py2exe = None


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
    'bottle >=0.11',
    'gevent >=0.13',
    'gevent-websocket >=0.9',
    'netifaces >=0.8',
    'zeroconf >=0.17']

# The directories in which the packages can be found
PACKAGE_DIR = {
    'virtualtouchpad': 'lib/virtualtouchpad'}

# Arguments passed to setup
setup_arguments = {}


def setup(**kwargs):
    global INFO, README, CHANGES, PACKAGE_DATA, PACKAGE_DIR
    setuptools.setup(
        cmdclass=dict(build.cmdclass),
        name='virtual-touchpad',
        version='.'.join(str(i) for i in INFO['version']),
        description='Turns your mobile or tablet into a touchpad for your '
        'computer.',
        long_description=README + '\n\n' + CHANGES,

        install_requires=REQUIREMENTS + platform_requirements(),

        setup_requires=REQUIREMENTS + platform_requirements() + [
            'cssmin',
            'ply ==3.4',
            'polib >=1.0.4',
            'slimit'],

        author=INFO['author'],
        author_email='moses.palmer@gmail.com',

        url='https://github.com/moses-palmer/virtual-touchpad',

        packages=setuptools.find_packages(
            os.path.join(
                os.path.dirname(__file__),
                'lib')),
        package_dir=PACKAGE_DIR,
        package_data=PACKAGE_DATA,
        zip_safe=True,

        license='GPLv3',
        platforms=['linux', 'windows'],
        classifiers=[],

        **kwargs)


def platform_requirements():
    """A list of PyPi packages that are dependencies only for the current
    platform.
    """
    platform = ''.join(c for c in sys.platform if c.isalpha())
    result = []

    if platform == 'linux':
        result.append('Pillow')
        if sys.version_info.major == 3:
            result.append('python3-xlib')
        elif sys.version_info.major == 2:
            result.append('python-xlib')
        else:
            raise NotImplementedError(
                'This python major version (%d) is not supported',
                sys.version_info.major)

    elif platform == 'win' or platform == 'cygwin':
        result.append('pywin32')

    else:
        raise NotImplementedError(
            'This platform (%s) is not supported',
            sys.platform)

    return result


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


try:
    # Read README
    with open(os.path.join(
            os.path.dirname(__file__),
            'README.rst')) as f:
        README = f.read()

    # Read CHANGES
    with open(os.path.join(
            os.path.dirname(__file__),
            'CHANGES.rst')) as f:
        CHANGES = f.read()
except IOError:
    README = ''
    CHANGES = ''


@build.utility
class xgettext(setuptools.Command):
    description = 'update the POT files'
    user_options = []

    def initialize_options(self): pass

    def finalize_options(self): pass

    def run(self):
        source_dir = build.HTML_ROOT
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
            messages = build.translation.read_translatable_strings(full_path)
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

                build.translation.merge_catalogs(potfile, pofile)


@build.command
class minify_index(setuptools.Command):
    description = 'minify index.xhtml'
    user_options = []

    def initialize_options(self): pass

    def finalize_options(self): pass

    def run(self):
        # Load index.html
        dom_context = build.xmltransform.start(
            os.path.join(
                build.HTML_ROOT,
                'index.xhtml'))

        # Minify the index file
        build.xmltransform.minify_html(dom_context)

        # Add the manifest file
        build.xmltransform.add_manifest(
            dom_context,
            'virtual-touchpad.appcache')

        # Write index.min.xhtml
        build.xmltransform.end(
            dom_context,
            os.path.join(
                build.HTML_ROOT,
                'index.min.xhtml'))


@build.command
class minify_help(setuptools.Command):
    description = 'minify help/index.xhtml'
    user_options = []

    def initialize_options(self): pass

    def finalize_options(self): pass

    def run(self):
        # Load help.xhtml
        dom_context = build.xmltransform.start(
            os.path.join(
                build.HTML_ROOT,
                'help',
                'index.xhtml'))

        # Minify the index file
        build.xmltransform.minify_html(dom_context)

        # Write help.min.xhtml
        build.xmltransform.end(
            dom_context,
            os.path.join(
                build.HTML_ROOT,
                'help',
                'index.min.xhtml'))


@build.command
class generate_webapp_icons(setuptools.Command):
    description = 'generate web application icons from SVG sources'
    user_options = []

    def initialize_options(self): pass

    def finalize_options(self): pass

    def run(self):
        # Generate the application icons
        for size in (196, 144, 114, 96, 72, 57, 48):
            build.icons.app_icon(
                size,
                os.path.join(
                    build.HTML_ROOT,
                    'img',
                    'icon%dx%d.png' % (size, size)))


@build.command
class generate_windows_icons(setuptools.Command):
    description = 'generate Windows icons from SVG sources'
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
            build.icons.app_icon(
                size,
                os.path.join(
                    target_dir,
                    'icon%dx%d.ico' % (size, size)))
        build.icons.combine(
            os.path.join(
                    target_dir,
                    'icon-all.ico'),
            *(os.path.join(
                    target_dir,
                    'icon%dx%d.ico' % (size, size))
                for size in self.DIMENSIONS))


@build.command
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


if py2exe:
    import virtualtouchpad.platform.win32 as win

    @build.command
    class extract_local_eggs(setuptools.Command):
        description = 'extract local egg files to allow py2exe to use them'
        user_options = []

        def initialize_options(self): pass

        def finalize_options(self): pass

        def run(self):
            import glob
            import zipfile

            for path in glob.glob('*.egg') + glob.glob('.*/*.egg'):
                # If it is not a ZIP file, this is not an egg module
                try:
                    zf = zipfile.ZipFile(path, 'r')
                except:
                    continue

                try:
                    # Create a temporary target directory and unzip the egg
                    target = path + '.tmp'
                    if not os.path.isdir(target):
                        os.mkdir(target)
                    zf.extractall(target)
                finally:
                    zf.close()

                # Rename the files
                os.rename(path, path + '.bak')
                os.rename(target, path)

    # Construct the data_files argument to setup from the package_data argument
    # value; py2exe does not support data files
    class py2exe_with_resources(py2exe.build_exe.py2exe):
        def copy_extensions(self, extensions):
            py2exe.build_exe.py2exe.copy_extensions(self, extensions)

            from glob import glob

            # Collect all package data files
            files = []
            for package, package_dir in PACKAGE_DIR.items():
                for pattern in PACKAGE_DATA.get(package, []):
                    files.extend((
                            f,
                            os.path.join(
                                package,
                                os.path.relpath(f, package_dir)))
                        for f in glob(os.path.join(package_dir, pattern)))

            # Copy the data files to the collection directory, and add the
            # copied files to the list of compiled files to ensure that they
            # will be included in the zip file
            for source, target in files:
                full_target = os.path.join(self.collect_dir, target)
                try:
                    os.makedirs(os.path.dirname(full_target))
                except OSError:
                    pass
                self.copy_file(source, full_target)
                self.compiled_files.append(target)

    build.cmdclass['py2exe'] = py2exe_with_resources

    setup_arguments['zipfile'] = None
    setup_arguments['options'] = {
        'py2exe': {
            'bundle_files': 1,
            'excludes': [
                'netifaces',
                'zeroconf'],
            'includes': [
                'greenlet',
                'gevent.select',
                'virtualtouchpad.platform.win32',
                'virtualtouchpad.event.win32',
                'virtualtouchpad.systray.win32',
                'virtualtouchpad.systray.win32.win32systray'] + [
                    'virtualtouchpad.server.dispatchers.%s' % m.rsplit('.')[0]
                    for m in os.listdir(
                        os.path.join(
                            'lib', 'virtualtouchpad', 'server',
                            'dispatchers'))
                    if not m.startswith('_') and m.endswith('.py')]}}
    setup_arguments['console'] = [
        'scripts/virtualtouchpad-console.py']
    setup_arguments['windows'] = [
        {
            'script': 'scripts/virtualtouchpad.py',
            'icon_resources': [(win.IDI_MAINICON, 'build/icos/icon-all.ico')]}]


setup(**setup_arguments)
