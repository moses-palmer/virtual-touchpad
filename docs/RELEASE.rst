How to make a release
=====================

There are a few simple steps to make a release.
  1. Run ``python scripts/make-release.py <version>``.
  2. Tag the commit on the format ``git tag -a -m "Release X.Y" vX.Y``.
  3. Push to origin.
  4. Run ``python ./setup.py sdist upload`` to update the package on PyPi.
