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
from hwtest.registry import Registry


class DataRegistry(Registry):
    """Base registry for storing data.

    The default behavior is to simply return the data passed as argument
    to the constructor.
    """

    def __init__(self, config, data=None):
        super(DataRegistry, self).__init__(config)
        self.data = data

    def __str__(self):
        return self.data

    def items(self):
        return []
