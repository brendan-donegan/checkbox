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
from datetime import datetime

from checkbox.plugin import Plugin


class DatetimeInfo(Plugin):

    def register(self, manager):
        super(DatetimeInfo, self).register(manager)

        self._manager.reactor.call_on("report", self.report)

    def report(self):
        message = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        self._manager.reactor.fire("report-datetime", message)


factory = DatetimeInfo
