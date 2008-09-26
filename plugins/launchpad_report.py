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
import os

from checkbox.lib.safe import safe_make_directory

from checkbox.plugin import Plugin
from checkbox.reports.launchpad_report import LaunchpadReportManager


class LaunchpadReport(Plugin):

    required_attributes = ["filename"]

    def register(self, manager):
        super(LaunchpadReport, self).register(manager)
        self._report = {
            "summary": {
                "private": False,
                "contactable": False,
                "live_cd": False},
            "hardware": {},
            "software": {
                "packages": []},
            "questions": []}

        # Launchpad report should be generated last.
        self._manager.reactor.call_on("report", self.report, 100)
        for (rt, rh) in [
             ("report-architecture", self.report_architecture),
             ("report-client", self.report_client),
             ("report-datetime", self.report_datetime),
             ("report-distribution", self.report_distribution),
             ("report-hal", self.report_hal),
             ("report-packages", self.report_packages),
             ("report-processors", self.report_processors),
             ("report-system_id", self.report_system_id),
             ("report-results", self.report_results)]:
            self._manager.reactor.call_on(rt, rh)

    def report_architecture(self, architecture):
        self._report["summary"]["architecture"] = architecture

    def report_hal(self, hal):
        self._report["hardware"]["hal"] = hal

    def report_client(self, client):
        self._report["summary"]["client"] = client

    def report_datetime(self, datetime):
        self._report["summary"]["date_created"] = datetime

    def report_distribution(self, distribution):
        self._report["software"]["lsbrelease"] = dict(distribution)
        self._report["summary"]["distribution"] = distribution.distributor_id
        self._report["summary"]["distroseries"] = distribution.release

    def report_packages(self, packages):
        self._report["software"]["packages"].extend(packages)

    def report_processors(self, processors):
        self._report["hardware"]["processors"] = processors

    def report_system_id(self, system_id):
        self._report["summary"]["system_id"] = system_id

    def report_results(self, results):
        for result in results:
            test = result.test
            question = dict(test.attributes)
            question["command"] = str(test.command)
            question["description"] = str(test.description)
            question["requires"] = str(test.requires)
            question["result"] = dict(result.attributes)
            self._report["questions"].append(question)

    def report(self):
        # Prepare the payload and attach it to the form
        report_manager = LaunchpadReportManager("system", "1.0")
        payload = report_manager.dumps(self._report).toprettyxml("")

        filename = self._config.filename
        directory = os.path.dirname(filename)
        safe_make_directory(directory)

        open(filename, "w").write(payload)
        self._manager.reactor.fire("exchange-report", filename)


factory = LaunchpadReport
