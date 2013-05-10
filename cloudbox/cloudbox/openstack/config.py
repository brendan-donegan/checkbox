"""
Copyright (C) 2013 Canonical Ltd.

Authors
  Jeff Marcom <jeff.marcom@canonical.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3,
as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import configparser
import logging


DEFAULT_CFG = "/etc/cloudbox.d/openstack.cfg"


class OpenstackConfigParser:
    """
    This is a simple parser class that will return the options
    and values defined for the openstack environment.
    """

    def __init__(self, config_file=DEFAULT_CFG):
        self.config_file = config_file
        self.parse()

    def parse(self):
        self._load_config()

        for section in self.config.sections():
            set_options = {}
            try:
                for field in self.config.options(section):
                    set_options[field] = self.config.get(section, field)
            except configparser.Error as configFieldException:
                logging.error(configFieldException)
                return

            self.add_property(section, set_options)

    def _load_config(self):

        try:
            self.config = configparser.SafeConfigParser()
            self.config.readfp(open(self.config_file))
        except IOError as configFileNotFound:
            logging.error(configFileNotFound)

    def add_property(self, section, fields):
        setattr(self, section, fields)
