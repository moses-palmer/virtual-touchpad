How to make a release
=====================

There are a few simple steps to make a release.
  1. Run ``python scripts/make-release.py <version>``.
  2. Make sure that the release note in ``./CHANGES.rst`` are up to date.
  3. Commit all changes.
  4. Tag the commit on the format ``git tag -a -m "Release X.Y" vX.Y``.
  5. Push to origin.
  6. Run ``python ./setup.py sdist upload`` to update the package on PyPi.
