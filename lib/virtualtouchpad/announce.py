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

import zeroconf.dns
import zeroconf.mdns

from ._platform import _freeze_modules
_freeze_modules(zeroconf.dns, 'socket')
_freeze_modules(zeroconf.mdns, 'socket')

from ._info import __version__


# The name of the Virtual Touchpad service
SERVICE_NAME = '_virtualtouchpad._http._tcp.local.'


def announce(ip_address, port):
    """
    Announces that Virtual Touchpad is available on the local network.

    @param ip_address
        The IP address on which Virtual Touchpad is reachable.
    @param port
        The port on which to connect to Virtual Touchpad.
    @return an object with the method 'unregister()', which must be called to
        remove the service from the system
    """
    import getpass
    import socket
    import types

    result = zeroconf.mdns.Zeroconf('0.0.0.0')
    info = zeroconf.dns.ServiceInfo(
        SERVICE_NAME,
        '%s@%s.%s' % (getpass.getuser(), socket.gethostname(), SERVICE_NAME),
        socket.inet_aton(ip_address),
        port,
        0, 0, # weight, priority
        {
            'version': '.'.join(str(v) for v in __version__)})
    result.registerService(info)

    def unregister(self):
        """
        Unregisters the Virtual Touchpad service.
        """
        self.unregisterService()
        self.close()

    result.unregister = types.MethodType(unregister, result)

    return result
