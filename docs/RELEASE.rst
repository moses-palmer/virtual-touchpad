How to make a release
=====================

There are a few simple steps to make a release.
  1. Run ``python scripts/make-release.py <version>``.
  2. Commit all changes.
  3. Tag the commit on the format ``git tag -a -m "Release X.Y" vX.Y``.
  4. Push to origin.
  5. Run ``python ./setup.py sdist upload`` to update the package on PyPi.
