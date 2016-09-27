import setuptools


#: A store of all build commands registered with :func:`build_command`
CMDCLASS = {}


def build_command(decorated):
    """Registers a class as a build command.

    :param decorated: The command class, or a descripttion string.
    """
    def inner(cls):
        if cls is not decorated:
            cls.description = decorated
        CMDCLASS[cls.__name__] = cls
        return cls

    if callable(decorated):
        return inner(decorated)
    else:
        return inner


class Command(setuptools.Command):
    """Convenience class to avoid having to define all required fields.
    """
    user_options = []
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)
