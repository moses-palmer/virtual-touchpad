Release Notes
=============

v0.15.3 - Fixes for OSX
---------------------------
*  Enabled dragging on *OSX*.
*  Increased scrolling speed on *OSX*.


v0.15.2 - Fixes for Windows
---------------------------
*  Reenabled clicking and scrolling for *Windows*.


v0.15.1 - Fixes for iOS
-----------------------
*  Do not require the browser to support *HTML5 Fullscreen*, since this is not
   supported on *iOS*.
*  Allow the application to run unpackaged again.


v0.15 - Python 3 Support
------------------------
*  Added support for Python 3.


v0.14 - System tray icon on Mac OSX
-----------------------------------
*  Added support for system tray icon on Mac OSX by replacing internal system
   tray icon handling with pystray_.

.. _pystray: https://pypi.python.org/pypi/pystray


v0.13 - Mac OSX Support
-----------------------
*  Added support for *Mac OSX* by replacing internal keyboard and mouse handling
   with pynput_ and, for now, making the systray icon optional.

.. _pynput: https://pypi.python.org/pypi/pynput


v0.12.4 - Corrected packaging
-----------------------------
*  Ensure that only dependencies for the current platform are required.
*  Allow loading the *systray icon* for *Windows* when running from a wheel.


v0.12.3 - Corrected clicks
--------------------------
*  Corrected touch pad clicks.


v0.12.2 - Corrected imports
---------------------------
*  Corrected imports.


v0.12.1 - No more PIL
---------------------
*  Replaced dependency on *PIL* with *Pillow*. This should make it possible to
   install from *PyPi*.


v0.12 - Shiny Keyboard
----------------------
*  Support for keyboards has been added. For now only two layouts are included.
*  The user interface has been polished.
*  *Virtual Touchpad* now broadcasts its presence on the network using *mDNS*.


v0.11 - Translations
--------------------
*  *Virtual Touchpad* can now be translated into other languages.
*  Added *Swedish* translation.


v0.10 - Systray on Windows
--------------------------
*  Added systray icon for *Windows*.


v0.9.2 - Fixed building on Windows
----------------------------------
*  *Virtual Touchpad* now supports zip-safe again.
*  The build script does not fail if *ImageMagick* ``convert`` is not the first
   ``convert`` on the path.


v0.9.1 - Fixed systray window on Linux
--------------------------------------
*  The systray window is no longer mapped on *Linux*.


v0.9 - Systray on Linux
-----------------------
*  Added systray icon for *Linux*.


v0.8 - Configure sensitivity
----------------------------
*  The sensitivity and acceleration of the trackpad is now configurable.
*  Clicking is now easier and allows the finger to move slightly across the
   screen.


v0.7 - Run from single file
---------------------------
*  *Virtual Touchpad* can now be run from a zipped egg.
*  Py2exe is now supported to pack *Virtual Touchpad* into a single exe file on
   *Windows*.


v0.6 - Windows support
----------------------
*  It is now possible to run *Virtual Touchpad* on *Windows*.


v0.5 - Installation possible
----------------------------
*  Corrected snapping of bottom tool bar.
*  Corrected bugs in setup script that prevented *Virtual Touchpad* from being
   installed.


v0.4 - Basic help
-----------------
*  Made scrolling a lot smoother.
*  Added basic *FAQ*.


v0.3 - Extended user interface
------------------------------
*  Added support for *drag-and-drop*.
*  Added a bottom toolbar with a fullscreen button.
*  Increased size of message box text.


v0.2 - Initial release
----------------------
*  Basic touchpad support, with hard-coded sensitivity and acceleration.
*  Basic offline support using *AppCache*.
