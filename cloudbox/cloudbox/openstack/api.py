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
:mod:`cloudbox.openstack.api` -- API access to Openstack
========================================================
"""

import json
import logging
import requests

from cloudbox.openstack.config import OpenstackConfigParser


component_mapping = {
    "glance": "Image",
    "keystone": "Identity",
    "nova": "Compute",
    "storage": "Volume"}

command_mapping = {
    "Identity": {
        "get_auth_token": ["tokens", "POST"],
        "list_tenants": ["tenants", "GET"]},
    "Compute": {
        "create_server": ["servers", "POST"],
        "server_console": ["servers", "POST"],
        "list_servers": ["servers", "GET"],
        "list_flavors": ["flavors", "GET"]},
    "Image": {
        "add_image": ["v2/images", "POST"],
        "upload_image": ["v2/images", "PUT"],
        "list_images": ["v2/images", "GET"]},

}


class API(object):
    """This class interacts with Openstack's component API
    endpoints. Default component API endpoints and methods
    are predefined. Sometimes you will need to add on to the
    predefined endpoint with a specific url tac.

    Example

    :/v2/images (Displays details for all images)
    :/v2/images/<image-id> (Displays details for a specific image)

    Adding an image-id, server-id, action request, etc can
    be done via supplying the string to page_tac

    Please see the documentation provided here for more API info

    :http://api.openstack.org/api-ref.html"""

    def __init__(self, component):
        self.openstack_config = OpenstackConfigParser()
        self.component = component
        self.token = ""
        self.authenticated = False
        self.base_header = {"Content-Type": "application/json"}
        self.binary_header = {"Content-Type": "application/octet-stream"}
        self.auth_header = {}
        self.data_header = {}
        self.page_tac = ""
        self._get_auth_token()

    def _get_credentials(self):
        """Grabs needed authentication credentials via openstack
        config module and returns them in acceptable json/header format"""

        username = self.openstack_config.Identity["username"]
        password = self.openstack_config.Identity["password"]
        tenant_id = self.openstack_config.Identity["tenant_id"]

        credentials = {
            "auth": {
                "passwordCredentials": {
                    "username": username,
                    "password": password},
                "tenantId": tenant_id
            }
        }

        return json.dumps(credentials)

    def _get_auth_token(self):
        """Retrieves authentication token based on supplied
        openstack dashboard tenantid"""
        logging.debug("Attempting to retrieve authentication token...")
        params = self._get_credentials()
        self.token = self.request(
            "get_auth_token", params)['access']['token']['id']
        self.authenticated = True

    def send_binary(self, command, file, params=""):
        service_type = component_mapping[self.component]
        url = getattr(self.openstack_config, service_type)["endpoint"]

        files = {'file': open(file, 'rb')}
        request_commands = command_mapping[service_type][command]
        page = request_commands[0] + self.page_tac

        target = "/".join((url, page))

        headers = dict(
            list(self.auth_header.items())
            + list(self.binary_header.items()))

        response = requests.put(target, files=files, headers=headers)
        logging.debug(response.status_code)
        logging.debug(response.text)

    def request(self, command, params=""):
        """Retrieves data from Openstack's RESTFUL API. Enpoints are defined
        and pulled from the config module and the command mapping dictates
        whether the supposed request is a GET or POST method. If you are
        modifying an image you'd need to specify the approprite API command
        and the meta data via the params argument to properly change an image.
        """

        url = self.openstack_config.Identity["endpoint"]
        headers = self.base_header
        service_type = "Identity"

        if self.authenticated:
            # Update Header values, intended url for component endpoint
            # reset component service type and supply newly created
            # authentication token
            logging.debug("Authenticated")
            service_type = component_mapping[self.component]
            url = getattr(self.openstack_config, service_type)["endpoint"]
            self.auth_header = {"X-Auth-Token": self.token}
            headers = dict(
                list(self.auth_header.items())
                + list(self.base_header.items())
                + list(self.data_header.items()))

        # Retrieve expected method and page per service component
        # Example: list_images, would use a "GET" method at /images
        request_commands = command_mapping[service_type][command]
        page = request_commands[0] + self.page_tac

        target = "/".join((url, page))
        method = request_commands[1].lower()

        logging.debug(getattr(requests, method))
        logging.debug("Retrieving API request info via: {}".format(target))
        response = getattr(requests, method)(
            target,
            data=params,
            headers=headers)

        logging.debug(headers)
        logging.debug(response)

        # assume that content is a json reply
        try:
            data = response.json()
        except (ValueError, AttributeError):
            data = response.text

        logging.debug(data)
        return data


def main():
    # DEBUG TESTS
    openstack_api = API
    #API("glance").get("list_images")
    #print(openstack_api("glance").request("list_images"))
    #API("keystone").request("list_tenants")["tenants"]


if __name__ == "__main__":
    main()
