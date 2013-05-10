#!/usr/bin/env python3
# This file is part of Checkbox.
#
# Copyright 2013 Canonical Ltd.
# Written by:
#   Jeff Marcom <jeff.marcom@canonical.com>
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

"""
:mod:`cloudbox.openstack.cli` -- CLI access to Openstack
========================================================
"""

from subprocess import Popen, PIPE
import json
import logging
import shlex
import sys

from cloudbox.openstack.config import OpenstackConfigParser


class CLI(object):

    def __init__(self, component):
        self.openstack_config = OpenstackConfigParser()
        # Authorization parameters
        self.username = self.openstack_config.Identity["username"]
        self.password = self.openstack_config.Identity["password"]
        self.tenant_name = self.openstack_config.Identity["tenant_name"]
        self.auth_url = self.openstack_config.Identity["endpoint"]
        self.component = component

    def format_to_json(output):
        """This reformats the nasty table data that we are
        given when running via openstack's component command
        line tools into a nice parseable json format"""

        data_set = output[1].split("|")
        column_headers = []
        line_sep = "+-----"

        # Break column headers away from table
        for line in data_set[1:]:
            if line_sep in line:
                break
            column_headers.append(line.strip())

        # Separate row data from rest of table
        row_data = [item.strip() for item in
                    data_set[(len(column_headers) + 1):]
                    if line_sep not in item]

        # Set result basket dictionary and feeder dictionary
        formatted_query = {}
        result_basket = {}
        column = 0
        row = 0

        for i in range(0, len(row_data)):
            if row_data[i] != "":
                # Update feeder dictionary
                formatted_query[column_headers[column]] = row_data[i]
                column += 1
                if column >= len(column_headers):
                    row += 1
                    column = 0
                # Add updated feeder to new entry in result dictionary
                result_basket[row] = formatted_query

        try:
            data = json.dumps(result_basket)
        except ValueError as parse_exception:
            logging.debug("Could not parse output as expected")
            logging.error(parse_exception)
            return

        return data

    def execute(self, command, params=""):

        auth_params = " ".join((
            "--os-username", self.username,
            "--os-password", self.password,
            "--os-tenant-name", self.tenant_name,
            "--os-auth-url", self.auth_url))

        action = " ".join((
            self.component,
            auth_params,
            command,
            params))

        logging.debug("command: %s" % shlex.split(action))

        result = Popen(
            shlex.split(action),
            stderr=PIPE, stdout=PIPE,
            universal_newlines=True)

        error, output = result.communicate()
        action_output = error + output

        print(action_output, file=sys.stderr)

        return result.returncode, action_output


def main():
    # DEBUG TESTS
    openstack_api = CLI


if __name__ == "__main__":
    main()
