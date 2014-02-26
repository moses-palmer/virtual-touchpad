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


def main():
    pass


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        try:
            sys.stderr.write(e.args[0] % e.args[1:] + '\n')
        except:
            sys.stderr.write('%s\n' % str(e))
        sys.exit(1)
