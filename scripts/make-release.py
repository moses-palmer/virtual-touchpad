#!/usr/bin/env python

import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _util import *

PACKAGE_NAME = 'virtualtouchpad'


def main():
    version = get_version()

    assert_clean()
    assert_current_branch()
    update_info(version)
    try:
        update_appcache(version)
        try:
            check_readme()
            check_release_notes(version)
            commit_changes(version)
            try:
                tag_release(version)
            except:
                commit_changes.undo()
                raise
            push_to_origin()
            upload_to_pypi()
        except:
            update_appcache.undo()
            raise
    except:
        update_info.undo()
        raise


def get_version():
    """Returns the version to set, read from the command line.

    :return: the tuple (v1, v2,...)
    """
    try:
        return tuple(int(p) for p in sys.argv[1].split('.'))
    except IndexError:
        raise RuntimeError('You must pass the version as the first argument')
    except:
        raise RuntimeError('Invalid version: %s', sys.argv[1])


def assert_current_branch():
    """Asserts that the current branch is *master* and contains no local
    changes.

    :raises AssertionError: if the current branch is not master

    :raises RuntimeError: if the repository contains local changes
    """
    assert git('rev-parse', '--abbrev-ref', 'HEAD').strip() == 'master', \
        'The current branch is not master'


def update_info(version):
    """Updates the version information in ``._info.``

    :param tuple version: The version to set.
    """
    gsub(
        update_info.path,
        re.compile(r'__version__\s*=\s*(\([0-9]+(\s*,\s*[0-9]+)*\))'),
        1,
        lambda m: repr(version))

update_info.path = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    'lib', PACKAGE_NAME, '_info.py')

def _update_info_undo():
    git('co',
        '-f',
        update_info.path)
update_info.undo = _update_info_undo


def update_appcache(version):
    """Updates the version information in the appcache file.

    :param tuple version: The version to set.
    """
    gsub(
        update_appcache.path,
        re.compile(r'\#\s*Version\s*([0-9]+(\.[0-9]+)*)'),
        1,
        lambda m: '.'.join(str(v) for v in version))

update_appcache.path = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    'lib', PACKAGE_NAME, 'html', 'virtual-touchpad.appcache')

def _update_appcache_undo():
    git('co',
        '-f',
        update_appcache.path)
update_appcache.undo = _update_appcache_undo


def check_readme():
    """Verifies that the ``README`` is *reStructuredText* compliant.
    """
    subprocess.check_call([
        'python', 'setup.py', 'check', '--restructuredtext', '--strict'])


def check_release_notes(version):
    """Displays the release notes and allows the user to cancel the release
    process.

    :param tuple version: The version that is being released.
    """
    CHANGES = os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        'CHANGES.rst')
    header = 'v%s' % '.'.join(str(v) for v in version)

    # Read the release notes
    found = False
    release_notes = []
    with open(CHANGES) as f:
        for line in (l.strip() for l in f):
            if found:
                if not line:
                    # Break on the first empty line after release notes
                    break
                elif set(line) == {'-'}:
                    # Ignore underline lines
                    continue
                release_notes.append(line)

            elif line.startswith(header):
                # The release notes begin after the header
                found = True

    while True:
        # Display the release notes
        sys.stdout.write('Release notes for %s:\n' % header)
        sys.stdout.write(
            '\n'.join(
                '  %s' % release_note
                for release_note in release_notes) + '\n')
        sys.stdout.write('Is this correct [yes/no]? ')
        sys.stdout.flush()
        response = sys.stdin.readline().strip()
        if response in ('yes', 'y'):
            break
        elif response in ('no', 'n'):
            raise RuntimeError('Release notes are not up to date')


def commit_changes(version):
    """Commits all local changes.

    :param tuple version: The version that is being released.
    """
    git('commit',
        '-a',
        '-m', 'Release %s' % '.'.join(str(v) for v in version))


def _commit_changes_undo():
    git('reset',
        '--hard',
        'HEAD^')
commit_changes.undo = _commit_changes_undo


def tag_release(version):
    """Tags the current commit as a release.

    :param version: The version that is being released.
    :type version: tuple of version parts
    """
    git('tag',
        '-a',
        '-m', 'Release %s' % '.'.join(str(v) for v in version),
        'v' + '.'.join(str(v) for v in version))


def push_to_origin():
    """Pushes master to origin.
    """
    print('Pushing to origin...')

    git('push', 'origin', 'HEAD:master')
    git('push', '--tags')


def upload_to_pypi():
    """Uploads this project to PyPi.
    """
    print('Uploading to PyPi...')

    g = subprocess.Popen(
        [
            'python',
            os.path.join(os.path.dirname(__file__), os.pardir, 'setup.py'),
            'bdist_wheel',
            'upload'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = g.communicate()
    if g.returncode != 0:
        raise RuntimeError(
            'Failed to upload to PyPi (%d): %s',
            g.returncode, stderr)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        try:
            sys.stderr.write(e.args[0] % e.args[1:] + '\n')
        except:
            sys.stderr.write('%s\n' % str(e))
        sys.exit(1)
