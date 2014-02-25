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
                if getattr(c, '__build_ignore', True):
                    continue
                self.run_command(name)
            super(self.__class__, self).run()

        # Create the command class, override run, and set __build_ignore to make
        # sure none of these command classes invoke each other
        this_class = command(type(name, (super_class, object), dict(run = run)))
        this_class.__build_ignore = True

_register_commands()


with open(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        os.pardir,
        'LICENSE')) as f:
    LICENSE = f.read()


from . import icons
from . import xmltransform
