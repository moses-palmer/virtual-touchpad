How to make a release
=====================

There are a few simple steps to make a release.
  1. Run ``python scripts/make-release.py <version>``.
  2. Push to origin.
  3. Run ``python ./setup.py sdist upload`` to update the package on PyPi.
