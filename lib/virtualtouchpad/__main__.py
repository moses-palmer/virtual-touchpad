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

from argparse import ArgumentParser

from . import main, systray

if __name__ == '__main__':
    parser = ArgumentParser(
        description = ''
            'Turns your mobile or tablet into a touchpad and keyboard for your '
            'computer.')

    parser.add_argument('--port',
        type = int,
        help = ''
            'The port on which to listen',
        default = 16080)

    args = parser.parse_args()
    icon = systray.create('Virtual Touchpad - http://%s:%d' % (
        socket.gethostname(), args.port))
    main(**vars(args)).serve_forever()
    systray.destroy(icon)
