How to make a release
=====================

There are a few simple steps to make a release.
  1. Run ``python scripts/make-release.py <version>``.
  2. Update ``./lib/virtualtouchpad/html/virtual-touchpad.appcache`` to reflect
     the new version. The comment should contain the new version, but it must at
     least be changed to allow clients to upgrade.
  3. Make sure that the release note in ``./CHANGES.rst`` are up to date.
  4. Commit all changes.
  5. Tag the commit on the format ``git tag -a -m "Release X.Y" vX.Y``.
  6. Push to origin.
  7. Run ``python ./setup.py sdist upload`` to update the package on PyPi.
