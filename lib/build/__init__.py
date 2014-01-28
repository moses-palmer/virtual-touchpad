import os
import sys


cmdclass = {}
_ignored = []

def command(c):
    """
    Registers a Command class as a build subcommand that should be run when
    building.

    @param c
        The class to use as a build sub command.
    """
    global cmdclass
    cmdclass[c.__name__] = c
    c.__build_ignore = False

    return c

def _register_commands():
    """
    Registers overrides for built in build commands.
    """
    from distutils.command.build import build
    from setuptools.command.bdist_egg import bdist_egg
    from setuptools.command.sdist import sdist

    # locals() at this point contains only the imported symbols
    for name, super_class in locals().items():
        # Define the run override
        def run(self):
            global cmdclass
            for name, c in cmdclass.items():
                if c.__build_ignore:
                    continue
                self.run_command(name)
            super(self.__class__, self).run()

        # Create the command class, override run, and set __build_ignore to make
        # sure none of these command classes invoke each other
        this_class = command(type(name, (super_class, object), dict(run = run)))
        this_class.__build_ignore = True

_register_commands()

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


# Read CHANGES
with open(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        os.pardir,
        'CHANGES')) as f:
    CHANGES = f.read()


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


from . import icons
from . import xmltransform

