#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of Checkbox.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
import unittest

from checkbox.config import Config


class TestHelper(unittest.TestCase):

    config_path = "./configs/checkbox.ini"
    config_section = "checkbox/registries"

    def setUp(self):
        section_test_class_name = self.__class__.__name__
        section_class_name = section_test_class_name.replace("Test", "")
        section_name = section_class_name.replace("Registry", "").lower()

        config = Config(self.config_path)
        self._config = config.get_section("%s/%s" \
            % (self.config_section, section_name))
