# This file is part of Checkbox.
#
# Copyright 2012-2013 Canonical Ltd.
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
:mod:`plainbox.impl.commands.script` -- script sub-command
==========================================================

.. warning::

    THIS MODULE DOES NOT HAVE STABLE PUBLIC API
"""

from logging import getLogger
from tempfile import TemporaryDirectory
import os

from plainbox.impl.applogic import NameJobQualifier, get_matching_job_list
from plainbox.impl.checkbox import CheckBox
from plainbox.impl.commands import PlainBoxCommand
from plainbox.impl.runner import JobRunner


logger = getLogger("plainbox.commands.script")


class _CommandInvocation:
    """
    Helper class instantiated to perform a particular invocation of the script
    command. Unlike :class:`ScriptCommand` this class is instantiated each time
    the command is to be invoked.
    """

    def __init__(self, config, job_name):
        self.config = config
        self.job_name = job_name
        self.checkbox = CheckBox()

    def run(self):
        job = self._get_job()
        if job is None:
            print("There is no job called {!a}".format(self.job_name))
            print("See `plainbox special --list-jobs` for a list of choices")
            return 126
        elif job.command is None:
            print("Selected job does not have a command")
            return 125
        with TemporaryDirectory() as scratch, TemporaryDirectory() as iologs:
            runner = JobRunner(scratch, iologs)
            runner._run_command(job, self.config)
            self._display_side_effects(scratch)

    def _display_file(self, pathname, origin):
        filename = os.path.relpath(pathname, origin)
        print("Leftover file detected: {!a}:".format(filename))
        with open(pathname, 'rt', encoding='UTF-8') as stream:
            for lineno, line in enumerate(stream, 1):
                line = line.rstrip('\n')
                print("\t{}:{}: {}".format(filename, lineno, line))

    def _display_side_effects(self, scratch):
        for dirpath, dirnames, filenames in os.walk(scratch):
            for filename in filenames:
                self._display_file(
                    os.path.join(dirpath, filename), scratch)

    def _get_job(self):
        job_list = get_matching_job_list(
            self.checkbox.get_builtin_jobs(),
            NameJobQualifier(self.job_name))
        if len(job_list) == 0:
            return None
        else:
            return job_list[0]
        job = job_list[0]



class ScriptCommand(PlainBoxCommand):
    """
    Command for running the `command` of a job unconditionally.
    """

    def __init__(self, config):
        self.config = config

    def invoked(self, ns):
        return _CommandInvocation(self.config, ns.job_name).run()

    def register_parser(self, subparsers):
        parser = subparsers.add_parser(
            "script", help="run a command from a job")
        parser.set_defaults(command=self)
        parser.add_argument(
            'job_name', metavar='JOB-NAME',
            help="Name of the job to run")
