#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of HWTest.
#
# HWTest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HWTest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HWTest.  If not, see <http://www.gnu.org/licenses/>.
#
from hwtest.lib.cache import cache

from hwtest.registries.command import CommandRegistry


class LsbRegistry(CommandRegistry):
    """Registry for LSB information.

    Each item contained in this registry consists of the information
    returned by the lsb_release command.
    """

    default_map = {
        "Distributor ID": "distributor_id",
        "Description": "description",
        "Release": "release",
        "Codename": "codename"}

    def __init__(self, config, filename=None, map=None):
        super(LsbRegistry, self).__init__(config, filename)
        self.map = map or self.default_map

    @cache
    def items(self):
        items = []
        for line in [l for l in self.split("\n") if l]:
            (key, value) = line.split(":\t", 1)
            if key in self.map:
                key = self.map[key]
                items.append((key, value))

        return items


factory = LsbRegistry
