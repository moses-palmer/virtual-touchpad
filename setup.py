#!/usr/bin/env python
# coding: utf8

def setup(**kwargs):
    global INFO, README, CHANGES, PACKAGE_DATA, PACKAGE_DIR
    setuptools.setup(
        cmdclass = dict(build.cmdclass),
        name = 'virtual-touchpad',
        version = '.'.join(str(i) for i in INFO['version']),
        description = ''
            'Turns your mobile or tablet into a touchpad for your computer.',
        long_description = README + '\n\n' + CHANGES,

        install_requires = [
            'bottle >=0.11',
            'gevent >=0.13',
            'gevent-websocket >=0.9'] + platform_requirements(),
        setup_requires = [
            'cssmin',
            'slimit'],

        author = INFO['author'],
        author_email = 'moses.palmer@gmail.com',

        url = 'https://github.com/moses-palmer/virtual-touchpad',

        packages = setuptools.find_packages(
            os.path.join(
                os.path.dirname(__file__),
                'lib'),
            exclude = [
                'build']),
        package_dir = PACKAGE_DIR,
        package_data = PACKAGE_DATA,
        zip_safe = True,

        license = 'GPLv3',
        platforms = ['linux', 'windows'],
        classifiers = [],

        **kwargs)


# Make sure we can import build
import os
import sys
sys.path.append(os.path.join(
    os.path.dirname(__file__),
    'lib'))

try:
    import build
except ImportError:
    class build:
        cmdclass = {}

        @staticmethod
        def command(c):
            return c

import setuptools

try:
    import py2exe
except ImportError:
    py2exe = None


def platform_requirements():
    """
    A list of PyPi packages that are dependencies only for the current platform.
    """
    platform = ''.join(c for c in sys.platform if c.isalpha())
    result = []

    if platform == 'linux':
        result.append('PIL')
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


# Data for the package; this will not be evaluated until the build steps have
# completed
PACKAGE_DATA = {
    'virtualtouchpad': [
        'html/*.*',
        'html/css/*.*',
        'html/img/*.*',
        'html/js/*.*']}

# The directories in which the packages can be found
PACKAGE_DIR = {
    'virtualtouchpad': 'lib/virtualtouchpad'}

# The directory in which HTML resources are located
HTML_ROOT = os.path.join(
    os.path.dirname(__file__),
    'lib',
    'virtualtouchpad',
    'html')


# Arguments passed to setup
setup_arguments = {}


@build.command
class minify_index(setuptools.Command):
    description = 'minify index.xhtml'
    user_options = []
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        global HTML_ROOT

        # Load index.html
        dom_context = build.xmltransform.start(
            os.path.join(
                HTML_ROOT,
                'index.xhtml'))

        # Minify the index file
        build.xmltransform.minify_html(dom_context)

        # Add the manifest file
        build.xmltransform.add_manifest(dom_context,
            'virtual-touchpad.appcache')

        # Write index.min.xhtml
        build.xmltransform.end(dom_context,
            os.path.join(
                HTML_ROOT,
                'index.min.xhtml'))


@build.command
class minify_help(setuptools.Command):
    description = 'minify help.xhtml'
    user_options = []
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        global HTML_ROOT

        # Load help.xhtml
        dom_context = build.xmltransform.start(
            os.path.join(
                HTML_ROOT,
                'help.xhtml'))

        # Minify the index file
        build.xmltransform.minify_html(dom_context)

        # Write help.min.xhtml
        build.xmltransform.end(dom_context,
            os.path.join(
                HTML_ROOT,
                'help.min.xhtml'))


@build.command
class generate_icons(setuptools.Command):
    description = 'generate web application icons from SVG sources'
    user_options = []
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        # Generate the application icons
        for size in (196, 144, 114, 72, 57):
            build.icons.app_icon(
                size,
                os.path.join(
                    HTML_ROOT,
                    'img',
                    'icon%dx%d.png' % (size, size)))


if py2exe:
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
                name = os.path.basename(target)
                self.copy_file(source, full_target)
                self.compiled_files.append(target)

    build.cmdclass['py2exe'] = py2exe_with_resources


    setup_arguments['zipfile'] = None
    setup_arguments['options'] = {
        'py2exe': {
            'bundle_files': 1,
            'includes': [
                'greenlet',
                'gevent.select',
                'virtualtouchpad._platform.event._win'] + [
                    'virtualtouchpad.dispatchers.%s' % m.rsplit('.', 1)[0]
                        for m in os.listdir(
                            os.path.join(
                                'lib', 'virtualtouchpad', 'dispatchers'))
                        if not m.startswith('_') and m.endswith('.py')]}}
    setup_arguments['console'] = [
        'scripts/virtualtouchpad-console.py']


try:
    setup(**setup_arguments)
except Exception as e:
    try:
        sys.stderr.write(e.args[0] % e.args[1:] + '\n')
    except:
        sys.stderr.write(str(e) + '\n')
