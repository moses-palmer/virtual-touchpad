#!/usr/bin/env python
# coding: utf8

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


def platform_requirements():
    """
    A list of PyPi packages that are dependencies only for the current platform.
    """
    platform = ''.join(c for c in sys.platform if c.isalpha())
    result = []

    if platform == 'linux':
        if sys.version_info.major == 3:
            result.append('python3-xlib')
        elif sys.version_info.major == 2:
            result.append('python-xlib')
        else:
            raise NotImplementedError(
                'This python major version (%d) is not supported',
                sys.version_info.major)

    elif platform == 'win' or platform == 'cygwin':
        pass

    else:
        raise NotImplementedError(
            'This platform (%s) is not supported',
            sys.platform)

    return result


def setup():
    global INFO, README, CHANGES
    setuptools.setup(
        cmdclass = dict(build.cmdclass),
        name = 'virtual-touchpad',
        version = '.'.join(str(i) for i in INFO['version']),
        description = ''
            'Turns your mobile or tablet into a touchpad and keyboard for your '
            'computer.',
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
        package_dir = {
            'virtualtouchpad': 'lib/virtualtouchpad'},
        package_data = {
            'virtualtouchpad': [
                'html/*.*',
                'html/css/*.*',
                'html/img/*.*',
                'html/js/*.*']},

        license = 'GPLv3',
        platforms = ['linux', 'windows'],
        classifiers = [])


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


HTML_ROOT = os.path.join(
    os.path.dirname(__file__),
    'lib',
    'virtualtouchpad',
    'html')


@build.command
class minify_index(setuptools.Command):
    description = 'minify index.xhtml'
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
    description = 'minify html.xhtml'
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


setup()
