# coding=utf-8
# virtual-touchpad
# Copyright (C) 2013-2015 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import contextlib
import logging
import os
import pkg_resources
import socket
import sys

import PIL.Image
import pystray

import virtualtouchpad.routes
import virtualtouchpad.resource as resource

from argparse import ArgumentParser

from virtualtouchpad import server
from ._info import __version__


# The name of the Virtual Touchpad service
SERVICE_NAME = '_virtualtouchpad._http._tcp.local.'

log = logging.getLogger('virtualtouchpad')


def _get_local_address(default=socket.gethostname()):
    """Returns the address for the local network.

    The one returned is the one most likely on a *LAN*.

    If no probable match is found, or an error occurs, ``default`` is returned.

    :param default: The default return value if none can be calculated.
    :type default: str

    :return: the address
    """
    try:
        import netifaces
    except ImportError:
        return default

    # Get all interfaces
    interfaces = {
        interface: netifaces.ifaddresses(interface)
        for interface in netifaces.interfaces()}

    # Get all IPv4 interfaces
    interfaces4 = {
        key: value[netifaces.AF_INET]
        for key, value in interfaces.items()
        if netifaces.AF_INET in value}

    # Get the IP address with the longest net mask
    best_length = 0
    result = None
    for interface, descriptions in interfaces4.items():
        for description in descriptions:
            if not 'broadcast' in description:
                continue

            # Count the number of non-0 in the net mask
            current_length = len([
                p
                for p in description['netmask'].split('.')
                if int(p)])
            if current_length < best_length:
                continue

            best_length = current_length
            result = description

    if result:
        return result['addr']
    else:
        return default


@contextlib.contextmanager
def _announcer(ip_address, port):
    """Announces that *Virtual Touchpad* is available on the local network.

    This function works as a context manager that unregisters the service upon
    exit.

    :param str ip_address: The IP address on which *Virtual Touchpad* is
        reachable.

    :param int port: The port on which to connect to *Virtual Touchpad*.
    """
    import getpass
    import socket
    import types

    try:
        import zeroconf
    except:
        yield
        return

    zc = zeroconf.Zeroconf()
    info = zeroconf.ServiceInfo(
        SERVICE_NAME,
        '%s@%s.%s' % (getpass.getuser(), socket.gethostname(), SERVICE_NAME),
        socket.inet_aton(ip_address),
        port,
        0, 0,
        {
            'version': '.'.join(str(v) for v in __version__)})
    zc.register_service(info)

    try:
        yield
    finally:
        zc.unregister_service(info)
        zc.close()


def start():
    parser = ArgumentParser(
        description='Turns your mobile or tablet into a touchpad for your '
        'computer.')

    parser.add_argument(
        '--port',
        type=int,
        help='The port on which to listen',
        default=16080)

    parser.add_argument(
        '--log-level',
        type=str,
        help='The log level to use.',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        default='error')

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()))

    address = _get_local_address()
    icon = pystray.Icon(
        __name__,
        title='Virtual Touchpad - http://%s:%d' % (
            address, args.port),
        icon=PIL.Image.open(
            resource.open_stream(
                'favicon.png')))

    try:
        def setup(icon):
            sys.stdout.write('Starting server http://%s:%d/...\n' % (
                address, args.port))
            main_server = server(args.port, address)
            icon.visible = True
            main_server.serve_forever()

        with _announcer(address, args.port):
            icon.run(setup)
    except KeyboardInterrupt:
        log.info('Interrupted, terminating')
    except:
        log.exception('An unhandler exception occurred in main')

if __name__ == '__main__':
    try:
        start()
    except Exception as e:
        log.exception('An unhandled exception occurred')
