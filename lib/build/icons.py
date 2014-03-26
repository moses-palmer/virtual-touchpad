import os
import subprocess
import sys


try:
    has_imagemagick = 'ImageMagick' in subprocess.check_output([
        'convert', '--version'])
except OSError:
    has_imagemagick = False

if has_imagemagick:
    def convert(source, target, dimensions):
        """
        Converts and resizes an image.

        @param source, target
            The source and target files.
        @param dimensions
            The dimensions for the target image.
        @raise RuntimeError if the conversion fails
        """
        p = subprocess.Popen(['convert',
            '-background', 'none',
            source,
            '-resize', 'x'.join(str(dimension) for dimension in dimensions),
            target],
            stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise RuntimeError('Failed to call convert: %s', stderr)

else:
    def convert(source, target, dimensions):
        """
        A no-op placeholder function.
        """
        sys.stdout.write('Not converting %s to %s: ImageMagick is not installed'
            % (source, target) + '\n')


def app_icon(size, target_path):
    """
    Creates an application icon PNG.

    @param size
        The required size of the output.
    @param target
        The output target.
    """
    # Create a PNG image from ./res/icon; its size is 16 px
    convert(
        os.path.join(
            os.path.dirname(__file__),
            'res',
            'icon.svg'),
        target_path,
        (size, size))
