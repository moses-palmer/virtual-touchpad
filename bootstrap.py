#!/usr/bin/env python

import os
import subprocess
import sys


if sys.version_info < (3, 5):
    print('Only Python 3.5 and later are supported.')
    sys.exit(1)


DIR = os.path.dirname(__file__) or '.'
PLATFORM = ''.join(c for c in sys.platform if c.isalpha())
VIRTUALENVDIR = os.path.join('venv', '%s-%d.%d' % (
    PLATFORM, sys.version_info.major, sys.version_info.minor))

def rel(path):
    return os.path.join(DIR, path)

COMMANDS = {
    'darwin': [rel('scripts/bootstrap/main.sh')],
    'linux': [rel('scripts/bootstrap/main.sh')],
    'win': ['cmd', '/C', rel('scripts\\bootstrap\\main.bat')]}[PLATFORM]

ACTIVATOR = {
    'darwin': '. %s/bin/activate' % VIRTUALENVDIR,
    'linux': '. %s/bin/activate' % VIRTUALENVDIR,
    'win': 'call %s\\Scripts\\activate.bat' % VIRTUALENVDIR}[PLATFORM]


try:
    subprocess.check_call(
        COMMANDS + [VIRTUALENVDIR, sys.executable],
        cwd=DIR)
    print('''
Successfully bootstrapped! Run this command to activate the virtualenv:

    %s
''' % ACTIVATOR)

except subprocess.CalledProcessError as e:
    sys.exit(e.returncode)
