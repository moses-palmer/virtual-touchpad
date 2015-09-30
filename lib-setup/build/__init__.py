import os


cmdclass = {}
_ignored = []


def command(c):
    """Registers a ``Command`` class as a build subcommand that should be
        run when building.

    :param type c: The class to use as a build sub command.
    """
    global cmdclass
    cmdclass[c.__name__] = c
    c.__build_ignore = False

    return c


def utility(c):
    """ Registers a ``Command`` class as a build subcommand.

    :param type c: The class to use as a build sub command.
    """
    global cmdclass
    cmdclass[c.__name__] = c
    c.__build_ignore = True

    return c


def _register_commands():
    """Registers overrides for built in build commands.
    """
    from distutils.command.build import build
    from setuptools.command.bdist_egg import bdist_egg
    from wheel.bdist_wheel import bdist_wheel
    from setuptools.command.sdist import sdist

    # locals() at this point contains only the imported symbols
    for name, super_class in locals().items():
        # Define the run override
        def run(self):
            global cmdclass
            for name, c in cmdclass.items():
                if getattr(c, '__build_ignore', True):
                    continue
                self.run_command(name)
            super(self.__class__, self).run()

        # Create the command class, override run, and set __build_ignore to
        # make sure none of these command classes invoke each other
        this_class = command(type(name, (super_class, object), dict(run=run)))
        this_class.__build_ignore = True

_register_commands()


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
        'LICENSE')) as f:
    LICENSE = f.read()


from . import icons
from . import translation
from . import xmltransform
