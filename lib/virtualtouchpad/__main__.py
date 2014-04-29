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

def start():
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
        default = (socket.gethostname(), '0.0.0.0'),
        action = AddressAction)

    args = parser.parse_args()
    icon = systray.SystemTrayIcon('Virtual Touchpad - http://%s:%d' % (
        args.address[0], args.port))

    main(**vars(args)).serve_forever()

if __name__ == '__main__':
    start()
