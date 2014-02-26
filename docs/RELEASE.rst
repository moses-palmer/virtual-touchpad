How to make a release
=====================

There are a few simple steps to make a release.
  1. Run ``python scripts/make-release.py <version>``.
  2. Update ``./lib/virtualtouchpad/_info.py`` to reflect the new version.
  4. Update ``./lib/virtualtouchpad/html/virtual-touchpad.appcache`` to reflect
     the new version. The comment should contain the new version, but it must at
     least be changed to allow clients to upgrade.
  4. Make sure that the release note in ``./CHANGES.rst`` are up to date.
  5. Commit all changes.
  6. Tag the commit on the format ``git tag -a -m "Release X.Y" vX.Y``.
  7. Push to origin.
  8. Run ``python ./setup.py sdist upload`` to update the package on PyPi.
