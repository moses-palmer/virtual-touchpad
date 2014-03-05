How to make a release
=====================

Run ``python scripts/make-release.py <version>``.

This script will check that no local changes are present in the repository and
that the master branch is checked out.

It will then update all version information, make a release commit, tag it, push
it to origin and finally upload a release package to PyPi.
