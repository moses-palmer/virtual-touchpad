import os
import subprocess
import sys

from . import update_file_time


def _locate_convert():
    """Locates ``convert`` from *ImageMagick*.

    :return: the path to convert, or ``None``
    :rtype: str or None
    """
    for path in os.getenv('PATH').split(os.pathsep):
        try:
            full = os.path.join(path, 'convert')
            if b'ImageMagick' in subprocess.check_output([full, '--version']):
                return full
        except:
            pass


CONVERT_COMMAND = _locate_convert()

APP_ICON = os.path.join(
    os.path.dirname(__file__),
    'res',
    'icon.svg')

if CONVERT_COMMAND:
    def convert(source, target, dimensions):
        """Converts and resizes an image.

        :param str source: The source file.

        :param str target: The target file.

        :param dimensions: The dimensions for the target image.
        :type dimensions: (int, int)

        :raises RuntimeError: if the conversion fails
        """
        p = subprocess.Popen([
            CONVERT_COMMAND,
            '-background', 'none',
            source,
            '-resize', 'x'.join(str(dimension) for dimension in dimensions),
            target],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
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
