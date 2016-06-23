#!/bin/bash

set -e

# LC_ALL may not be set on OSX, and __PYVENV_LAUNCHER__ interferes with
# virtualenv
export LC_ALL=""${LC_ALL:-C}""
unset __PYVENV_LAUNCHER__


SCRIPTDIR="$(dirname $0)"
VIRTUALENV_DIR="$1"
PYTHON="$2"


# Create the virtualenv
"$PYTHON" -m virtualenv --python="$PYTHON" "$VIRTUALENV_DIR"


# Activate the virtualenv and install packages; make sure pip fails if we run
# outside of a virtualenv
export PIP_REQUIRE_VIRTUALENV=true
. "$VIRTUALENV_DIR/bin/activate"
python "$SCRIPTDIR/install-packages.py"
