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
import logging
import socket
import pprint


class HTTPTransport(object):
    """Transport makes a request to exchange message data over HTTP."""

    def __init__(self, url, pubkey=None):
        self._url = url
        self._pubkey = pubkey

    def get_url(self):
        return self._url

    def _post(self, payload, headers={}):
        """Actually POSTs the payload to the server."""

        import urllib2

        headers.setdefault("User-Agent", "hwtest")

        opener = urllib2.build_opener()
        opener.addheaders = list(headers.items())
        ret = opener.open(self._url, payload)
        return ret

    def exchange(self, payload, headers={}, timeout=0):
        """Exchange the payload with the server."""

        import urllib2

        ret = None
        if timeout:
            socket.setdefaulttimeout(timeout)
        try:
            ret = self._post(payload, headers)
        except urllib2.URLError:
            logging.exception("Error contacting the server")
        except urllib2.HTTPError:
            logging.exception("Failure submitting data to server")
            logging.error("Response headers: %s",
                          pprint.pformat(ret.headers.items()))
        else:
            if ret.code != 200:
                logging.error("Server returned non-expected code: %d" % ret.code)

        return ret


class StubTransport(object):
    """Fake transport for testing purposes."""

    def __init__(self):
        self.payloads = []
        self.responses = []
        self.next_expected_sequence = 0
        self.extra = {}

    def get_url(self):
        return ""

    def exchange(self, payload, headers={}):
        self.payloads.append(payload)
        self.next_expected_sequence += len(payload.get("messages", []))
        result = {"next-expected-sequence": self.next_expected_sequence,
                  "messages": self.responses}
        result.update(self.extra)
        return result

