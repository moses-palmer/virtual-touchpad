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

import gettext
import locale
import os

from . import resource


#: The root path for translations
ROOT = 'translations'

#: The default domain
DOMAIN = 'server'


class VTTranslations(gettext.GNUTranslations):
    #: The environment variables used to detect current language
    ENVVARS = ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG')

    def __init__(self, domain):
        """Initialises a translation catalogue for a specific domin.

        The catalogue is created from a resource loaded by
        :func:`virtualtouchpad.resource.stream_open`, and it must be located in
        the ``translations`` package.

        :param str domain: The domain. This is used as sub-directory name under
            ``translations``.
        """
        try:
            mo_file = self._mo_file(
                domain,
                self._locales(self.ENVVARS))
        except:
            mo_file = self._mo_file(
                domain,
                (
                    locale.split('_')[0]
                    for locale in self._locales(self.ENVVARS)))

        super().__init__(mo_file)

    def _mo_file(self, domain, locales):
        """Returns a file like object yielding the contents of the *MO* file to
        use.

        :param str domain: The domain to use.

        :param locales: The sequence of locales.

        :return: a file like object, or ``None``
        """
        return resource.open_stream(next(
            mo_file
            for mo_file in self._mo_files(domain, locales)
            if resource.exists(mo_file)))

    def _mo_files(self, domain, locales):
        """Returns a sequence of all *MO* files that could exists for a domain,
        given a sequence of locales.

        The returned resource names may not exist.

        :param str domain: The domain to use.

        :param locales: The sequence of locales.

        :return: a generator
        """
        return (
            os.path.join(ROOT, domain, '%s.mo' % locale)
            for locale in locales)

    def _locales(self, envvars):
        """Returns a sequence of normalised locales read from the environment
        variables.

        :param envvars: A sequence of environment variables to check.

        :return: a generator
        """
        return (
            locale.normalize(language).split('.')[0]
            for env in envvars
            if os.environ.get(env)
            for language in os.environ[env].split(':'))


# Create a translation instance and use it in the module scope
try:
    _translation = VTTranslations(DOMAIN)
except:
    _translation = gettext.NullTranslations()
_ = _translation.gettext
_N = _translation.ngettext
