import subprocess
import sys

import buildlib

from . import build_command, Command


@build_command('install node dependencies')
class node_dependencies(Command):
    PACKAGE_COMMAND = ['npm', 'install']

    def node(self):
        """Makes sure that node.js is installed"""
        sys.stdout.write('Checking node.js installation...\n')

        # Since node.js picked an already used binary name, we must check
        # whether "node" is node.js or node - Amateur Packet Radio Node program;
        # The former actually provides output for the --version command
        try:
            node_output = subprocess.check_output(['node', '--version']).decode(
                'utf8')
            if node_output.strip():
                sys.stdout.write(node_output)
                return
        except OSError:
            pass

        # On Debian, node is called nodejs because of the above mentioned clash
        try:
            subprocess.check_call(['nodejs', '--version'])
            return
        except OSError:
            pass

        sys.stderr.write('node.js is not installed; terminating\n')
        sys.exit(1)

    def npm(self):
        """Makes sure that npm is installed"""
        sys.stdout.write('Checking npm installation...\n')

        try:
            subprocess.call(['npm', '--version'])
        except OSError:
            sys.stderr.write('npm is not installed; terminating\n')
            sys.exit(1)

    def packages(self):
        """Makes sure that dependencies are installed locally"""
        sys.stdout.write('Checking dependencies...\n')

        # Try to install it
        try:
            subprocess.check_call(self.PACKAGE_COMMAND)
            return
        except (OSError, subprocess.CalledProcessError):
            sys.stderr.write('Failed to install dependencies; terminating\n')
            sys.exit(1)

    def run(self):
        self.node()
        self.npm()
        self.packages()
