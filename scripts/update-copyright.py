#!/usr/bin/env python

import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _util import *


COPYRIGHT_RE = re.compile(
    r'Copyright\s+\(C\)\s+(([0-9]{4})(\s*-\s*[0-9]{4})?)')


def main():
    assert_clean()

    replace_copyright()


def replace_copyright():
    """Replaces the copyright in every versioned file.
    """
    this = datetime.datetime.now().year

    def replacer(m):
        first = int(m.group(2))
        if first != this:
            return '%d-%d' % (first, this)
        else:
            return '%d' % this

    for path in paths():
        gsub(
            path,
            COPYRIGHT_RE,
            1,
            replacer)

    git('commit', '--all', '--message=Updated copyright')


def paths():
    for name in git('ls-tree', '-r', '--name-only', 'HEAD').splitlines():
        yield os.path.join(SOURCE_DIRECTORY, name.rstrip())


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        raise
        try:
            sys.stderr.write(e.args[0] % e.args[1:] + '\n')
        except:
            sys.stderr.write('%s\n' % str(e))
        sys.exit(1)
