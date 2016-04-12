import os


def update_file_time(target, *sources):
    """Updates the file modification times of a file to match the latest
    modification time in sources.

    :param str target: The target files whose times to update.

    :param str sources: The source files. If no source files are passed, no
        action is taken.
    """
    if not sources:
        return

    atime, mtime = 0, 0
    for source in sources:
        st = os.stat(source)
        atime = max(atime, st.st_atime)
        mtime = max(mtime, st.st_mtime)
    os.utime(target, (atime, mtime))


with open(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        os.pardir,
        'LICENSE'), 'rb') as f:
    LICENSE = f.read().decode('utf-8')

#: The directory in which *HTML* resources are located
HTML_ROOT = os.path.join(
    os.path.dirname(__file__),
    os.path.pardir,
    'virtualtouchpad',
    'html')


from . import icons
from . import translation
from . import xmltransform
