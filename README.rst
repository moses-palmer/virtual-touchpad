Virtual Touchpad
================

This application allows you to use a mobile phone or tablet as a touchpad for
your computer.

No software needs to be installed on the device.


How does it work?
-----------------

A simple HTTP server is started on the computer, and the device connects by
simply opening a URL in a browser.

To manually start the HTTP server, run the following command:

    python -m virtualtouchpad

This will start an HTTP server. It will print the line

    Starting server http://<computer name>:<port>/...

Open this URL on your device to start controlling your computer.


Installation
------------

Install this application by running the following command as root:

    pip install virtual-touchpad

If you want to have access to pre-release versions, you can clone the *git*
repository available from the linked *home page* below. Install by running this
command as root:

    cd $VIRTUAL_TOUCHPAD_REPO
    python setup.py install


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
