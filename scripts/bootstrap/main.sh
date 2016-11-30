#!/bin/bash

set -e


##
# Generates a canonical, absolute path from a file name.
#
# $1: path
#     The path of the file for which to generate a canonical name. If this is a
#     symlink, it will be followed recursively.
cannonical() {
    path="$2"

    while : ; do
        dir="$(dirname "$path")"
        base="$(basename "$path")"
        cd "$dir"
        test -L "$base" || break
        path="$(readlink "$(basename "$path")")"
    done

    echo "$(pwd -P)/$base"
}


# LC_ALL may not be set on OSX, and __PYVENV_LAUNCHER__ interferes with
# virtualenv
export LC_ALL=""${LC_ALL:-C}""
unset __PYVENV_LAUNCHER__


# Make sure the virtualenv directory exists
if [ ! -d "$1" ]; then
    mkdir -p "$1"
fi

SCRIPTDIR="$(dirname $0)"
VIRTUALENV_DIR="$(cannonical "$1")"
PYTHON="$2"


# Create the virtualenv
"$PYTHON" -m virtualenv --python="$PYTHON" "$VIRTUALENV_DIR"


# Activate the virtualenv and install packages; make sure pip fails if we run
# outside of a virtualenv
export PIP_REQUIRE_VIRTUALENV=true
. "$VIRTUALENV_DIR/bin/activate"
python "$SCRIPTDIR/install-packages.py"


# If we are not running on Mac OSX, we should install UI dependencies
if [ "$(uname)" != "Darwin" ]; then
    PREFIX="$VIRTUALENV_DIR" "$(dirname "$0")/install-gi.sh"
fi
