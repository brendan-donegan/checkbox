# This file is part of Checkbox.
#
# Copyright 2014 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
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

"""
plainbox.impl.test_mainloop
===========================

Test definitions for plainbox.impl.mainloop module
"""

from unittest import TestCase

from plainbox.impl.mainloop import Descriptor
from plainbox.impl.mainloop import Process
from plainbox.impl.mainloop import Timer
from plainbox.vendor import mock


class DescriptorTests(TestCase):
    """
    Unit tests for the Descriptor class
    """

    _FD = 7  # arbitrary number

    def setUp(self):
        self.descriptor = Descriptor(self._FD)

    def test_fd(self):
        """
        verify that reading the Descriptor.fd property works
        """
        self.assertEqual(self.descriptor.fd, self._FD)

    def test_fileno(self):
        self.assertEqual(self.descriptor.fileno(), self._FD)

    @mock.patch('os.close')
    def test_close(self, mock_close):
        self.descriptor.close()
        mock_close.assert_called_once()

    def test_repr(self):
        self.assertEqual(
            repr(self.descriptor), "<Descriptor fd:{}>".format(self._FD))


class TimerTests(TestCase):
    """
    Unit tests for the Timer class
    """

    _REMAINING = 3.5

    def setUp(self):
        self.timer = Timer(self._REMAINING)

    def test_remaining(self):
        """
        verify that reading Timer.remaining works
        """
        self.assertEqual(self.timer.remaining, self._REMAINING)

    def test_rearm(self):
        """
        verify that Timer.rearm() changes the remaining time
        """
        self.timer.rearm(10)
        self.assertEqual(self.timer.remaining, 10)
        self.timer.rearm(0)
        self.assertEqual(self.timer.remaining, 0)

    def test_rearm_negative(self):
        """
        verify that Timer.rearm() rejects negative values
        """
        with self.assertRaises(ValueError):
            self.timer.rearm(-1)

    def test_adjust(self):
        """
        verifty that Timer.adjst() can move the remaining time forward
        and backwards.
        """
        timer = Timer(10)
        timer.adjust(1)
        self.assertEqual(timer.remaining, 11)
        timer.adjust(-2)
        self.assertEqual(timer.remaining, 9)

    def test_adjust_fires_the_signal(self):
        """
        verify that Timer.adjust() fires the Timer.on_fire() signal
        when the time remaining drops below zero.
        """
        timer = Timer(1)
        self.fired = False

        def actually_fired():
            self.fired = True
        timer.on_fire.connect(actually_fired)
        self.assertFalse(self.fired)
        timer.adjust(-1)
        self.assertTrue(self.fired)

    def test_pending(self):
        """
        verify that Timer.pending is True before the time runs out
        """
        self.assertTrue(self.timer.pending)
        self.timer.adjust(-self.timer.remaining)
        self.assertFalse(self.timer.pending)

    def test_repr(self):
        """
        verify that Timer.__repr__() works
        """
        self.assertEqual(
            repr(self.timer), "<Timer remaining:{}>".format(self._REMAINING))


class ProcessTests(TestCase):
    """
    Unit tests for the Process class
    """

    _PID = 1234
    _NAME = "name"

    def setUp(self):
        self.process = Process(self._PID)

    def test_pid(self):
        """
        verify that reading Process.pid works
        """
        self.assertEqual(self.process.pid, self._PID)

    def test_name(self):
        """
        verify that reading and writing Process.name works
        """
        self.assertEqual(self.process.name, None)
        self.process.name = self._NAME
        self.assertEqual(self.process.name, self._NAME)

    def test_is_terminated(self):
        """
        verify that reading Process.is_terminated works
        """
        self.assertFalse(self.process.is_terminated, False)

    def test_is_suspended(self):
        """
        verify that reading Process.is_terminated works
        """
        self.assertFalse(self.process.is_suspended, False)

    def test_repr(self):
        """
        verify that Process.__repr__() works
        """
        self.assertEqual(
            repr(self.process),
            ("<Process pid:{} name:{!r} is_terminated:{}"
             " is_suspended:{}>").format(
                self.process.pid, self.process.name,
                self.process.is_terminated, self.process.is_suspended))
