#!/usr/bin/env python

import subprocess
import sys


def git(*args):
    """
    Executes git with the command line arguments given.

    @param args...
        The arguments to git.
    @return stdout of git
    @raise RuntimeError if git returns non-zero
    """
    g = subprocess.Popen(['git'] + list(args),
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    stdout, stderr = g.communicate()
    if g.returncode != 0:
        raise RuntimeError('Failed to call git %s (%d): %s',
            ' '.join(args),
            g.returncode, stderr)
    else:
        return stdout


def get_version():
    """
    Returns the version to set, read from the command line.

    @return the tuple (v1, v2,...)
    """
    try:
        return tuple(int(p) for p in sys.argv[1].split('.'))
    except IndexError:
        raise RuntimeError('You must pass the version as the first argument')
    except:
        raise RuntimeError('Invalid version: %s', sys.argv[1])


def main():
    version = get_version()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        try:
            sys.stderr.write(e.args[0] % e.args[1:] + '\n')
        except:
            sys.stderr.write('%s\n' % str(e))
        sys.exit(1)
