# coding=utf-8
# virtual-touchpad
# Copyright (C) 2013-2016 Moses Palmér
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

from ._util import static
from . import get


#: The root path for static resources
ROOT = 'html'

#: Special extensions which should be removed before determining the MIME type
#: of a file; the order is significant, as extensions will stripped one by one
#: in order
SPECIAL_EXTENSIONS = (
    'min',)

#: The files, in the preferred order, to use as index files
INDEX_FILES = (
    'index.xhtml.min',
    'index.xhtml')


@get('/')
@get('/{filepath:.*}')
async def file_resource(app, headers, filepath=''):
    return static(headers, ROOT, filepath, INDEX_FILES, SPECIAL_EXTENSIONS)
