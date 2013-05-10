# This file is part of Checkbox.
#
# Copyright 2012, 2013 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
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
:mod:`cloudbox.provider` -- CloudBox specific provider for PlainBox
===================================================================
"""

import collections
import inspect
import logging
import os

from plainbox.impl.checkbox import CheckBox

import cloudbox


logger = logging.getLogger("cloudbox.provider")


def _get_cloudbox_dir():
    """
    Return the root directory of the cloudbox source checkout
    """
    return os.path.normpath(
        os.path.join(
            os.path.dirname(
                inspect.getabsfile(cloudbox)), ".."))


class CloudBoxProvider(CheckBox):
    """
    Provider class exposing CloudBox jobs to PlainBox.
    """

    # Temporary helper to compute "src" value below
    source_dir = _get_cloudbox_dir()

    _DIRECTORY_MAP = collections.OrderedDict((
        # Layout for source checkout
        ("src", CheckBox.CheckBoxDirs(
            source_dir,
            os.path.join(source_dir, "scripts"),
            os.path.join(source_dir, "jobs"),
            os.path.join(source_dir, "data"))),
        # Layout for Ubuntu 12.10 and 13.04
        ("deb2", CheckBox.CheckBoxDirs(
            "/usr/share/cloudbox/",
            "/usr/lib/cloudbox/bin",
            "/usr/share/cloudbox/jobs",
            "/usr/share/cloudbox/data")),
        # Layout for Ubuntu 12.04
        ("deb1", CheckBox.CheckBoxDirs(
            "/usr/share/cloudbox/",
            "/usr/share/cloudbox/scripts",
            "/usr/share/cloudbox/jobs",
            "/usr/share/cloudbox/data"))))

    # Remove temporary helper that was needed above
    del source_dir
