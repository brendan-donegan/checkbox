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
from checkbox.plugin import Plugin


class AttachmentInfo(Plugin):

    def register(self, manager):
        super(AttachmentInfo, self).register(manager)

        self._manager.reactor.call_on("prompt-attachment",
            self.prompt_attachment)
        self._manager.reactor.call_on("report-attachment",
            self.report_attachment, -10)

    def report_attachment(self, attachment):
        attachment["type"] = "attachment"

    def prompt_attachment(self, interface, attachment):
        self._manager.reactor.fire("prompt-shell", interface, attachment)


factory = AttachmentInfo
