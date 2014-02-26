#!/usr/bin/env python

import os
import re
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


def gsub(path, regex, group, replacement):
    """
    Runs a regular expression on the contents of a file and replaces a group.

    @param path
        The path to the file.
    @param regex
        The regular expression to use.
    @param group
        The group of the regular expression to replace.
    @param replacement
        The replacement string.
    """
    with open(path) as f:
        data = f.read()

    def sub(match):
        full = match.group(0)
        o = match.start(0)
        return full[:match.start(group) - o] \
            + replacement \
            + full[match.end(group) - o:]

    with open(path, 'w') as f:
        f.write(regex.sub(sub, data))


def assert_current_branch_is_master_and_clean():
    """
    Asserts that the current branch is 'master' and contains no local changes.

    @raise AssertionError is the current branch is not master
    @raise RuntimeError if the repository contains local changes
    """
    assert git('rev-parse', '--abbrev-ref', 'HEAD').strip() == 'master', \
        'The current branch is not master'
    try:
        git('diff-index', '--quiet', 'HEAD', '--')
    except RuntimeError as e:
        print e.args[0] % e.args[1:]
        raise RuntimeError('Your repository contains local changes')


def update_info(version):
    """
    Updates the version information in virtualtouchpad._init.

    @param version
        The version to set.
    """
    gsub(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            'lib', 'virtualtouchpad', '_info.py'),
        re.compile(r'__version__\s*=\s*(\([0-9]+(\s*,\s*[0-9]+)*\))'),
        1,
        repr(version))


def main():
    version = get_version()

    assert_current_branch_is_master_and_clean()
    update_info(version)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        try:
            sys.stderr.write(e.args[0] % e.args[1:] + '\n')
        except:
            sys.stderr.write('%s\n' % str(e))
        sys.exit(1)
