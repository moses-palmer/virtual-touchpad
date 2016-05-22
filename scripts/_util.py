#!/usr/bin/env python

import os
import subprocess


SOURCE_DIRECTORY = os.path.join(
    os.path.dirname(__file__),
    os.path.pardir)


def git(*args):
    """Executes ``git`` with the command line arguments given.

    :param args: The arguments to ``git``.

    :return: stdout of ``git``

    :raises RuntimeError: if ``git`` returns non-zero
    """
    g = subprocess.Popen(
        ['git'] + list(args),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=SOURCE_DIRECTORY)

    stdout, stderr = g.communicate()
    if g.returncode != 0:
        raise RuntimeError(
            'Failed to call git %s (%d): %s',
            ' '.join(args),
            g.returncode, stderr)
    else:
        return stdout.decode('utf-8')


def assert_clean():
    """Asserts that the working tree is clean.

    :raises RuntimeError: if the working tree is not clean
    """
    try:
        git('diff-index', '--quiet', 'HEAD', '--')
    except RuntimeError as e:
        print(e.args[0] % e.args[1:])
        raise RuntimeError('Your repository contains local changes')


def gsub(path, regex, group, replacer):
    """Runs a regular expression on the contents of a file and replaces a
    group.

    :param str path: The path to the file.

    :param regex: The regular expression to use.

    :param int group: The group of the regular expression to replace.

    :param str replacement: The replacement string.
    """
    with open(path, 'rb') as f:
        old_data = f.read().decode('utf-8')

    def sub(match):
        full = match.group(0)
        o = match.start(0)
        return full[:match.start(group) - o] \
            + replacer(match) \
            + full[match.end(group) - o:]

    new_data = regex.sub(sub, old_data)
    with open(path, 'wb') as f:
        f.write(new_data.encode('utf-8'))
