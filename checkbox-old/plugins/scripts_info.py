#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.

#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
from checkbox.lib.environ import append_path, prepend_path

from checkbox.plugin import Plugin
from checkbox.properties import Path


class ScriptsInfo(Plugin):

    # Executable path for running scripts.
    scripts_path = Path(default="%(checkbox_share)s/scripts")

    def register(self, manager):
        super(ScriptsInfo, self).register(manager)

        self._manager.reactor.call_on("gather", self.gather, -1000)

    def gather(self):
        prepend_path(self.scripts_path)
        append_path("/sbin")
        append_path("/usr/sbin")


factory = ScriptsInfo
