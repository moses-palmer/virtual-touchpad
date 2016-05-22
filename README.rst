Virtual Touchpad
================

This application allows you to use a mobile phone or tablet as a touchpad and
keyboard for your computer.

No software needs to be installed on the device.


Quick Start
-----------

On *Windows*, you can use the pre-packaged binary ``virtualtouchpad.exe``. When
you run it, an icon will appear in the notification area. Hovering over this
icon reveals the URL to use on your phone or tablet.

If no pre-built executable exists for your platform, launch it from a terminal::

    python -m virtualtouchpad

This will start an HTTP server. It will print the line

    Starting server http://<computer name>:<port>/...

Connect to the URL displayed.


Installation
------------

Install this application by running the following command:

    pip install virtual-touchpad

If you want to have access to pre-release versions, you can clone the *git*
repository available from the linked *home page* below. Install by running this
command::

    cd $VIRTUAL_TOUCHPAD_REPO
    python bootstrap.py
    # Follow instructions to activate virtualenv
    python setup.py install

If you intend to run the build target ``build_exe``, you must activate the
*virtualenv*. This is to ensure that no optional dependencies for any libraries,
*PIL* in particular, are included from the host system. *PIL* contains import
statements for *Tk* and *Qt*, which will increase the size of the resulting
binary, and thus the download and startup times, considerably.


Installation issues
~~~~~~~~~~~~~~~~~~~

When installing, the dependencies for this application are also downloaded. Some
of the dependencies are native libraries and must be compiled before they can be
used.

There is no standard way of providing any dependencies for the native libraries
through this website, so they must thus be present on your computer before you
run the installation, as do *Python* development headers files.

The easies way to install the headers is via the packager manager provided by
your operating system. The names of the packages required depend on your
specific operating system.
