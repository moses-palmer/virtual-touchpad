import contextlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

from buildlib import BUILDDIR, HTML_ROOT, PDIR, update_file_time
from . import build_command, Command


@build_command('generates raster icons')
class generate_raster_icons(Command):
    # The icon source directory
    SOURCE_DIR = os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        'res')

    # The names of the icon files, relative to ``SOURCE_DIR`` and excluding the
    # file extension
    ICONS = ('icon-dark', 'icon-light')

    # The target directory for generated icons
    TARGET_DIR = os.path.abspath(os.path.join(
        BUILDDIR, 'icons'))

    # The icon dimensions to generate
    DIMENSIONS = (
        1024, 512, 256, 196, 144, 128, 114, 96, 72, 64, 57, 48, 32, 16)

    def run(self):
        if not os.path.isdir(self.TARGET_DIR):
            os.makedirs(self.TARGET_DIR)

        for name in self.ICONS:
            source_path = os.path.join(self.SOURCE_DIR, '%s.svg' % name)
            source_stat = os.stat(source_path)

            # Generate icons only for modified files
            for size in self.DIMENSIONS:
                target_path = self.icon_name(size, name)
                try:
                    target_stat = os.stat(target_path)
                    if not (source_stat.st_mtime > target_stat.st_mtime):
                        continue
                except:
                    pass
                convert(source_path, target_path, (size, size))

    @classmethod
    def icon_name(cls, dimension, name=ICONS[0]):
        """Generates the name of the generated icon of a specific dimension.

        :param int dimension: The size of the icon. This must be one of the
            values in :attr:`DIMENSIONS`.

        :param str name: The name to use as base name.

        :raises ValueError: if ``dimension`` is invalid
        """
        if dimension not in cls.DIMENSIONS:
            raise ValueError(dimension)
        return os.path.join(cls.TARGET_DIR, '%s%dx%d.png' % (
            name, dimension, dimension))


@build_command('generate a favicon from SVG sources',
               generate_raster_icons)
class generate_favicon(Command):
    BASE_ICO = 'favicon.ico'
    BASE_PNG = 'favicon.png'

    TARGET_DIR = HTML_ROOT

    TARGET_ICO = os.path.join(TARGET_DIR, BASE_ICO)
    TARGET_PNG = os.path.join(TARGET_DIR, BASE_PNG)

    DIMENSIONS = (128, 64, 32, 16)

    def run(self):
        Command.run(self)
        combine(
            self.TARGET_ICO,
            *(
                generate_raster_icons.icon_name(size)
                for size in self.DIMENSIONS))
        shutil.copy2(
            generate_raster_icons.icon_name(self.DIMENSIONS[0]),
            self.TARGET_PNG)


@build_command('generate a system tray icon from SVG sources',
               generate_raster_icons)
class generate_trayicon(Command):
    # The target directory for generated icons
    TARGET_DIR = PDIR

    # The raster icon dimension to use
    DIMENSION = 64

    def run(self):
        Command.run(self)
        for name in generate_raster_icons.ICONS:
            shutil.copy2(
                generate_raster_icons.icon_name(self.DIMENSION, name),
                os.path.join(self.TARGET_DIR, name + '.png'))


@build_command('generate the app icon for OSX',
               generate_raster_icons)
class generate_appicon_darwin(Command):
    BASE = 'icon-darwin.icns'

    TARGET_DIR = generate_raster_icons.TARGET_DIR

    TARGET = os.path.join(TARGET_DIR, BASE)

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
                    generate_raster_icons.icon_name(size))
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

    TARGET_DIR = generate_raster_icons.TARGET_DIR

    TARGET = os.path.join(TARGET_DIR, BASE)

    # The icon dimension to use
    DIMENSION = 128

    def run(self):
        Command.run(self)
        shutil.copy2(
            os.path.join(
                generate_raster_icons.icon_name(self.DIMENSION)),
            self.TARGET)


@build_command('generate the app icon for Windows',
               generate_raster_icons)
class generate_appicon_win(Command):
    BASE = 'icon-win.ico'

    TARGET_DIR = generate_raster_icons.TARGET_DIR

    TARGET = os.path.join(TARGET_DIR, BASE)

    # The icon dimensions to include
    DIMENSIONS = (128, 64, 32, 16)

    def run(self):
        Command.run(self)
        combine(
            self.TARGET,
            *(os.path.join(
                generate_raster_icons.icon_name(size))
                for size in self.DIMENSIONS))


@build_command('generate the app icon for all platforms',
               generate_appicon_darwin,
               generate_appicon_linux,
               generate_appicon_win)
class generate_appicon(Command):
    BASE = 'icon%dx%d.png'

    TARGET_DIR = os.path.abspath(os.path.join(
        HTML_ROOT,
        'img'))

    TARGET = os.path.join(TARGET_DIR, BASE)

    DIMENSIONS = (196, 144, 114, 72, 57)

    def run(self):
        Command.run(self)

        for size in self.DIMENSIONS:
            source_path = generate_raster_icons.icon_name(size)
            target_path = self.TARGET % (size, size)
            shutil.copy2(source_path, target_path)


@build_command('generates all icons',
               generate_favicon,
               generate_trayicon,
               generate_appicon)
class generate_icons(Command):
    pass


def _locate_binary(name, checker=lambda output: True):
    """Locates a binary.

    The binary in question must support being called with the single argument
    ``--version``. The fort one to reutn success of all binaries on ``$PATH`` is
    returned.

    :param str name: The name of the binary.

    :param callable checker: A function that is passed the output of running the
        command. It must return ``True`` if the output is correct.

    :return: the path to the binary, or ``None``
    :rtype: str or None
    """
    for path in os.getenv('PATH').split(os.pathsep):
        try:
            full = os.path.join(path, name)
            if checker(subprocess.check_output([full, '--version'])):
                return full
        except:
            pass


def _locate_convert():
    """Locates *convert* from *ImageMagick*.

    :return: the path to ``convert``, or ``None``
    :rtype: str or None
    """
    return _locate_binary(
        'convert',
        lambda output: b'ImageMagick' in output)


def _locate_phantomjs():
    """Locates *phantomjs*.

    :return: the path to ``phantonjs``, or ``None``
    :rtype: str or None
    """
    return _locate_binary('phantomjs')


CONVERT_COMMAND = _locate_convert()
PHANTOMJS_COMMAND = _locate_phantomjs()


if CONVERT_COMMAND:
    if PHANTOMJS_COMMAND:
        @contextlib.contextmanager
        def _preprocess(source, dimensions):
            """Converts an *SVG* file to a temporary *PNG* file.
            """
            if source.endswith('.svg'):
                path = tempfile.mktemp(suffix='.png')
                subprocess.Popen(
                    [
                        PHANTOMJS_COMMAND,
                        '--web-security=false',
                        os.path.join(
                            os.path.dirname(__file__),
                            'svg-converter.js')],
                    stdin=subprocess.PIPE).communicate(json.dumps({
                        'command': 'convert',
                        'args': {
                            'source': source,
                            'target': path,
                            'size': max(dimensions)}}).encode('utf-8'))

                try:
                    yield path
                finally:
                    os.unlink(path)

            else:
                yield source

    else:
        @contextlib.contextmanager
        def _preprocess(source, dimensions):
            """A no-op placeholder function.
            """
            sys.stdout.write(
                'Not preprocessing %s: PhantomJS is not installed' % (
                    source) + '\n')
            yield source

    def convert(source, target, dimensions):
        """Converts and resizes an image.

        :param str source: The source file.

        :param str target: The target file.

        :param dimensions: The dimensions for the target image.
        :type dimensions: (int, int)

        :raises RuntimeError: if the conversion fails
        """
        with _preprocess(source, dimensions) as preprocessed_source:
            p = subprocess.Popen([
                CONVERT_COMMAND,
                '-background', 'none',
                preprocessed_source,
                '-resize', '%s!' % 'x'.join(
                    str(dimension) for dimension in dimensions),
                target],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _, stderr = p.communicate()
            if p.returncode != 0:
                raise RuntimeError('Failed to call convert: %s', stderr)

            update_file_time(target, source)

    def combine(target, *icons):
        """Creates a combined *ICO* file.

        :param str target: The target icon.

        :param [str] icons: The icons to combine into one.
        """
        p = subprocess.Popen(
            [CONVERT_COMMAND] + list(icons) + [target],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise RuntimeError('Failed to call convert: %s', stderr)

        update_file_time(target, *icons)


else:
    def convert(source, target, dimensions):
        """A no-op placeholder function.
        """
        sys.stdout.write(
            'Not converting %s to %s: ImageMagick is not installed' % (
                source, target) + '\n')

    def combine(target, *icons):
        """A no-op placeholder function.
        """
        sys.stdout.write(
            'Not combining %s to %s: ImageMagick is not installed' % (
                ', '.join(icons), target) + '\n')
