# coding=utf-8
# virtual-touchpad
# Copyright (C) 2013-2017 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import enum

import virtualtouchpad._info as info

from .configuration.notifier import Notifier
from .configuration import Store, Value


class Configuration(Store):
    APPLICATION_VERSION = Value(
        'application.version',
        'The version of this application',
        default=lambda v: '.'.join(str(v) for v in info.__version__))
    SERVER_HOST = Value(
        'server.host',
        'The server hostname')
    SERVER_PORT = Value(
        'server.port',
        'The port of the server')
    SERVER_URL = Value(
        'server.url',
        'The URL of the server',
        default=lambda configuration: 'http://{}:{}/'.format(
            configuration.SERVER_HOST,
            configuration.SERVER_PORT))
    ACCESS_TOKEN = Value(
        'access.token',
        'The use once access token',
        readonly=False,
        private=True)

    def __init__(self, **kwargs):
        super().__init__(Notifier(), **kwargs)
