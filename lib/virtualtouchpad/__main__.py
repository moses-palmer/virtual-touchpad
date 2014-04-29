# coding=utf-8
'''
virtual-touchpad
Copyright (C) 2013-2014 Moses Palmér

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
'''

import socket

from argparse import ArgumentParser, Action

from . import main, systray


def _get_bind_info():
    """
    Returns the name of the host and IP address to use as the tuple
    (name, address).

    The one returned is the one most likely on a LAN.

    If no probable match is found, the tuple (socket.gethostname(), '0.0.0.0')
    is returned.

    @return the tuple (name, address)
    """
    import netifaces

    # Get all interfaces
    interfaces = {interface: netifaces.ifaddresses(interface)
        for interface in netifaces.interfaces()}

    # Get all IPv4 interfaces
    interfaces4 = {key: value[netifaces.AF_INET]
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
            current_length = len([p
                for p in description['netmask'].split('.')
                if int(p)])
            if current_length < best_length:
                continue

            best_length = current_length
            result = interface, description

    if result:
        return (description['addr'], description['addr'])
    else:
        return (socket.gethostname(), '0.0.0.0')


def start():
    from . import announce

    parser = ArgumentParser(
        description = ''
            'Turns your mobile or tablet into a touchpad for your computer.')

    parser.add_argument('--port',
        type = int,
        help = ''
            'The port on which to listen',
        default = 16080)

    class AddressAction(Action):
        def __call__(self, parser, namespace, value, option_string = None):
            setattr(namespace, self.dest, (value, value))
    parser.add_argument('--address',
        type = str,
        help = ''
            'The IP address on which to listen',
        default = _get_bind_info(),
        action = AddressAction)

    args = parser.parse_args()
    icon = systray.SystemTrayIcon('Virtual Touchpad - http://%s:%d' % (
        args.address[0], args.port))

    announcer = announce.announce(args.address[1], args.port)
    try:
        main(**vars(args)).serve_forever()
    finally:
        announcer.unregister()

if __name__ == '__main__':
    try:
        start()
    except Exception as e:
        import sys
        try:
            sys.stderr.write('%s\n' % e.args[0] % e.args[1:])
        except TypeError:
            sys.stderr.write('%s\n' % str(e))
