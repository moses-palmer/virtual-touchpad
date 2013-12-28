import os
import sys

# Read globals from virtualtouchpad._info without loading it
info = {}
with open(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        'virtualtouchpad',
        '_info.py')) as f:
    for line in f:
        try:
            name, value = (i.strip() for i in line.split('='))
            if name.startswith('__') and name.endswith('__'):
                info[name[2:-2]] = eval(value)
        except ValueError:
            pass


# Read README
with open(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        os.pardir,
        'README')) as f:
    README = f.read()


def platform_requirements():
    """
    A list of PyPi packages that are dependencies only for the current platform.
    """
    platform = ''.join(c for c in sys.platform if c.isalpha())
    result = []

    # We only support linux
    if platform == 'linux':
        if sys.version_info.major == 3:
            result.append('python3-xlib')
        elif sys.version_info.major == 2:
            result.append('python-xlib')
        else:
            raise NotImplementedError(
                'This python major version (%d) is not supported',
                sys.version_info.major)

    else:
        raise NotImplementedError(
            'This platform (%s) is not supported',
            sys.platform)

    return result


from . import minify
