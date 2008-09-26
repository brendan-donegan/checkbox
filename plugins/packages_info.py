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
from checkbox.plugin import Plugin


class PackagesInfo(Plugin):

    required_attributes = ["max_per_request"]

    def register(self, manager):
        super(PackagesInfo, self).register(manager)
        self._max_per_request = int(self._config.max_per_request)
        self._manager.reactor.call_on("report", self.report)

    def report(self):
        packages = self._manager.registry.packages.values()
        while packages:
            message = packages[:self._max_per_request]
            del packages[:self._max_per_request]
            self._manager.reactor.fire("report-packages", message)


factory = PackagesInfo
