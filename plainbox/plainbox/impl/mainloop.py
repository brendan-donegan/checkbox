# Copyright 2014 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
:mod:`plainbox.impl.mainloop` -- simple mainloop system
=======================================================

Simple python-native mainloop implementation based on select.epoll.
Supported features include:

Input/Output Events:
 - IO operation possible

Process Events:
 - terminated (generic)
 - exited
 - killed by signal
 - suspended
 - resumed

Timer Events:
 - fired
"""

import errno
import fcntl
import logging
import os
import posix
import pty
import select
import signal
import time

from plainbox.impl.signal import Signal

_logger = logging.getLogger("plainbox.mainloop")

__all__ = ['MainLoop', 'Descriptor', 'Process', 'Timer']


class Descriptor:
    """
    A wrapper around a raw system descriptor with a given number.

    This class is useful to observe (wait for) possible IO a given descriptor,
    especially when coupled with :class:`MainLoop` and the
    :meth:`MainLoop.watch_descriptor()` method.
    """

    def __init__(self, fd):
        """
        Initialize a new :class:`Descriptor` instance with the given
        descriptor number
        """
        self._fd = fd

    @property
    def fd(self):
        """
        number of the descriptor
        """
        return self._fd

    def fileno(self):
        """
        Same as :attr:`Descriptor.fd`, provided due to common convention
        """
        return self.fd

    def close(self):
        """
        Close the descriptor with os.close()
        """
        os.close(self._fd)

    @Signal.define
    def on_io_possible(self, event_mask):
        """
        Signal fired when some io operation becomes possible.

        :param event_mask:
            The encoding, as defined by epoll(), of the event. Typically this
            is :attr:`posix.EPOLLIN` or :attr:`posix.EPOLLOUT` or similar.
        """

    def __repr__(self):
        return "<Descriptor fd:{}>".format(self.fd)


class Timer:
    """
    A timer that can fire in specified amount of seconds.

    Timers are single-use. That is, they expire and automatically get removed
    the main loop. To prevent this and create periodic timer, you can use the
    :meth:`Timer.rearm()` method from the :meth:`Timer.on_fire()` signal.
    """

    def __init__(self, remaining):
        self._remaining = remaining

    @property
    def remaining(self):
        """
        amount of seconds remaining, until this timer will fire

        This may be a negative amount if the timer has already fired
        """
        return self._remaining

    def rearm(self, remaining):
        """
        Re-arm the timer to fire after the specified amount of seconds

        :param remaining:
            Number of seconds to wait before firing
        :raises ValueError:
            If the number of seconds remaining is negative
        """
        if remaining < 0:
            raise ValueError("expected non-negative value")
        self._remaining = remaining

    def adjust(self, delta):
        """
        Adjust the number of remaining seconds.

        :param delta:
            Number of seconds to adjust by

        This method can be used to both extend the timer to fire at a later
        point as well as to make it fire sooner. It is used internally by
        the main loop after each iteration.

        If adjustment causes the timer to stop being pending, it will fire.
        """
        self._remaining += delta
        if not self.pending:
            self.on_fire()

    @property
    def pending(self):
        """
        flag indicating that this timer is yet to fire

        Timers are pending when the remaining time is greater than zero.
        Any negative remaining time or zero are considered to make the timer
        not "pending" anymore.
        """
        return self._remaining > 0

    @Signal.define
    def on_fire(self):
        """
        Signal fired when the timer runs out of time and fires
        """

    def __repr__(self):
        return "<Timer remaining:{}>".format(self.remaining)


class Process:
    """
    A wrapper around a raw system process with a given pid.

    This class is useful to observe process changes when coupled with
    :class:`MainLoop` and specifically the :meth:`MainLoop.watch_process()`
    method.
    """

    def __init__(self, pid, name=None):
        self._pid = pid
        self._name = name
        self._is_terminated = False
        self._is_suspended = False

    @property
    def pid(self):
        """
        identifier of the process
        """
        return self._pid

    @property
    def name(self):
        """
        name (optional) of the process, can be reassigned
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def is_terminated(self):
        """
        flag set to True when the process exits or gets killed
        """
        return self._is_terminated

    @property
    def is_suspended(self):
        """
        flag set to True when the process is suspended with SIGSTOP
        (and reset when that is undone with SIGCONT)
        """
        return self._is_suspended

    @classmethod
    def fork_and_execve(self, path, args, env):
        """
        Create a new process by forking and using :func:`posix.execve()`
        function.

        :param path:
            Full path of the executable to execute
        :param args:
            A list or tuple of arguments to pass, including the first one
            (process name)
        :param env:
            A dictionary with the environment to execute the process in
        :returns:
            a fresh :class:`Process` object
        """
        child_pid = os.fork()
        if child_pid == 0:
            try:
                posix.execve(path, args, env)
            except OSError as exc:
                _logger.error(exc)
                posix._exit(127)
        else:
            _logger.debug("spawned child: %d", child_pid)
            return Process(child_pid, args[0] if len(args) else None)

    def kill(self, signal_num=signal.SIGTERM):
        """
        Send a signal to the process.

        By default SIGTERM is being sent.
        """
        if not self.is_terminated:
            _logger.debug(
                "sending signal %d to process %r", signal_num, self)
            os.kill(self.pid, signal_num)

    @Signal.define
    def on_termination(self):
        """
        Signal fired when the process becomes terminated.

        Processes may either end normally or may be terminated by a signal.
        If you want to experience the signal-triggered termination, observe
        the :meth:`on_killed_by_signal` Signal, if you want to observe normal
        exits then observe :meth:`on_exit` signal instead. This signal is
        fired for *both* types of process termination.

        This signal is fired *after* either of the more specific signal are
        fired.
        """
        self._is_terminated = True

    @Signal.define
    def on_exit(self, exit_code):
        """
        Signal fired when a process exits normally
        """
        self._is_terminated = True
        _logger.debug("%r exited with code %d", self, exit_code)
        self.on_termination()

    @Signal.define
    def on_death_by_signal(self, signal_num):
        """
        Signal fired when the process is killed by a signal.
        """
        self._is_terminated = True
        _logger.debug("%r killed by signal %d", self, signal_num)
        self.on_termination()

    @Signal.define
    def on_suspend(self, signal_num):
        """
        Signal fired when the process becomes suspended by a signal
        """
        self._is_suspended = True
        _logger.debug("%r suspended by signal %d", self, signal_num)

    @Signal.define
    def on_resume(self):
        """
        Signal fired when the process becomes resumed by SIGCONT
        """
        self._is_suspended = False
        _logger.debug("%r resumed", self)

    def __repr__(self):
        return (
            "<Process pid:{} name:{!r} is_terminated:{}"
            " is_suspended:{}>").format(
            self.pid, self.name, self.is_terminated, self.is_suspended)


class _Pipe:
    """
    A wrapper around a pair of descriptors created with :func:`posix.pipe()`
    """

    def __init__(self, nonblock=False):
        read_end_fd, write_end_fd = posix.pipe()
        self.read_end = Descriptor(read_end_fd)
        self.write_end = Descriptor(write_end_fd)
        if nonblock:
            fcntl.fcntl(read_end_fd, fcntl.F_SETFL, posix.O_NONBLOCK)
            fcntl.fcntl(write_end_fd, fcntl.F_SETFL, posix.O_NONBLOCK)

    def close(self):
        self.read_end.close()
        self.write_end.close()


class PseudoTerminal:

    def __init__(self):
        self.master_fd, self.slave_fd = pty.openpty()

    def close(self):
        os.close(self.master_fd)
        os.close(self.slave_fd)


class _MainLoop_Base:
    """
    The base implementation of a MainLoop that has no features but provides
    all of the common high-level API.
    """

    def __init__(self):
        self._running = False
        self._cycle_count = 0

    @property
    def cycle_count(self):
        """
        number of cycles this loop has executed
        """
        return self._cycle_count

    @property
    def running(self):
        """
        flag indicating that the loop is currently executing
        """
        return self._running

    def run(self):
        """
        Run the main loop until it has nothing left to do.

        The "nothing to do" aspect is defined as the loop having at least
        one objeect to watch for.
        """
        self._running = True
        while self._should_keep_running():
            self.run_once()
        self._running = False

    def run_once(self):
        self._cycle_count += 1
        _logger.debug("starting_loop_iteration: %d", self._cycle_count)

    def _should_keep_running(self):
        """
        Determine if the loop should keep running for another iteration.

        This implementation always returns False as the loop cannot possibly
        do anything at this stage.
        """
        return False

    def close(self):
        pass

    def __repr__(self):
        return "<MainLoop id:{} running:{} cycle_count:{}>".format(
            id(self), self.running, self.cycle_count)


class _MainLoop_DescriptorManagement(_MainLoop_Base):
    """
    An in implementation of a MainLoop that supports watching descriptors.

    This class uses select.epoll object to poll for IO on any number of
    descriptors. Descriptors are wrapped in :class:`Descriptor` objects
    for API simplicity and existing PlainBox signal system is used
    for notification.
    """

    def __init__(self):
        super().__init__()
        self._descriptors = {}
        self._epoll = select.epoll()

    def close(self):
        self._epoll.close()
        super().close()

    def watch_descriptor(self, descriptor, event_mask):
        """
        Watch for operations on the specified descriptor.

        This is a high-level version of :meth:`select.epoll.register()` that
        uses a :class:`Descriptor` object instead of a raw integer.
        Notification is provided using :meth:`Descriptor.io_possible`.

        :param descriptor:
            A :class:`Descriptor` object to watch
        :param event_mask:
            A mask composed of EPOLLIN, EPOLLOUT and similar to watch for
        :raises:
            OSError if the descriptor is already being watched
        """
        if not isinstance(descriptor, Descriptor):
            raise TypeError("expected Descriptor instance")
        _logger.debug(
            "registering epoll notification for %r with mask %d",
            descriptor, event_mask)
        self._epoll.register(descriptor.fd, event_mask)
        self._descriptors[descriptor.fd] = descriptor

    def remove_descriptor_watch(self, descriptor):
        """
        Stop watching for operations on the specified descriptor.

        This is a high-level version of :meth:`select.epoll.unregister()`
        that uses a :class:`Descriptor` object instead of a raw integer.

        :param descriptor:
            A :class:`Descriptor` object to stop watching
        """
        if not isinstance(descriptor, Descriptor):
            raise TypeError("expected Descriptor instance")
        _logger.debug(
            "unregistering epoll notification for %r", descriptor)
        self._epoll.unregister(descriptor.fd)
        del self._descriptors[descriptor.fd]

    def modify_descriptor_watch(self, descriptor, event_mask):
        """
        Modify the event mask of a descriptor being watched.

        This is a high-level version of :meth:`select.epoll.modify()` that
        uses a :class:`Descriptor` object instead of a raw integer.

        :param descriptor:
            A :class:`Descriptor` object to watch
        :param event_mask:
            A mask composed of EPOLLIN, EPOLLOUT and similar to watch for
        """
        if not isinstance(descriptor, Descriptor):
            raise TypeError("expected Descriptor instance")
        _logger.debug(
            "modifying epoll notification for %r to new mask mask %d",
            descriptor, event_mask)
        if descriptor.fd not in self._descriptors:
            raise ValueError("unknown descriptor")
        self._epoll.modify(descriptor.fd, event_mask)

    def run_once(self):
        super().run_once()
        timeout = self._get_sleep_timeout()
        if timeout != -1 or self._descriptors:
            packed_event_list = self._do_poll(timeout)
            if packed_event_list:
                _logger.debug("processing descriptor events")
                for packed_event in packed_event_list:
                    self._process_epoll_event(packed_event)

    def _should_keep_running(self):
        retval = super()._should_keep_running() or bool(self._descriptors)
        _logger.debug("(descriptors) _should_keep_running() -> %r", retval)
        return retval

    def _do_poll(self, timeout):
        packed_event_list = ()
        try:
            _logger.debug("epoll.poll(%d) ...", timeout)
            packed_event_list = self._epoll.poll(timeout)
        except KeyboardInterrupt as exc:
            _logger.debug("epoll.poll(%d) *** %r", timeout, exc)
        except OSError as exc:
            _logger.debug("epoll.poll(%d) *** %r", timeout, exc)
            if exc.errno != errno.EINTR:
                raise
        _logger.debug("epoll.poll(%d) -> %r", timeout, packed_event_list)
        return packed_event_list

    def _process_epoll_event(self, packed_event):
        fd, events = packed_event
        _logger.debug("epoll event for fd: %r events: %r", fd, events)
        try:
            descriptor = self._descriptors[fd]
            descriptor.on_io_possible(events)
        except KeyError:
            _logger.warning("ignoring event on fd: %r", fd)

    def _get_sleep_timeout(self):
        return -1


class _MainLoop_TimerManagement(_MainLoop_DescriptorManagement):
    """
    An implementation of a MainLoop that supports setting timers
    """

    def __init__(self):
        super().__init__()
        self._timers = []

    def watch_timer(self, timer):
        """
        Watch for activity of the specified timer.

        :param timer:
            A :class:`Timer` object to watch
        :raises TypeError:
            If ``time`` is not an instance of :class:`Timer`

        After being added, on each loop iteration, each timer is adjusted
        with :meth:`Timer.adjust()`. Timers that expire are sending a signal
        that can be connected to your application.

        Timer can be added at most once. Calling :meth:`watch_timer()`
        with the same time multiple times is harmless.

        .. warning::
            Time spent outside of the loop is not taken into account yet.
            This is a bug that will be fixed at some point. Right now
            timers are inert and store the amount of seconds remaining.
            Ideally timers would instead store the absolute value of the
            monotonic clock at which they expire.
        """
        if not isinstance(timer, Timer):
            raise TypeError("expected Timer instance")
        if timer not in self._timers:
            self._timers.append(timer)

    def remove_timer_watch(self, timer):
        """
        Stop watching for activity of the specified timer.

        This method undoes the effects of :meth:`watch_process()`.

        :param timer:
            A :class:`Timer` object to stop watching
        :raises TypeError:
            If ``timer`` is not an instance of :class:`Timer`

        For API simplicity, it is safe to call this on a timer that is
        no longer being watched. Normally timers automatically un-watch
        themselves when they expire so it would make any kind of cleanup code
        cumbersome if a check was required around each call to this method.
        """
        if not isinstance(timer, Timer):
            raise TypeError("expected Timer instance")
        try:
            self._timers.remove(timer)
        except ValueError:
            pass

    def run_once(self):
        start_time = self._get_time()
        try:
            super().run_once()
        finally:
            end_time = self._get_time()
            # NOTE: delta is _negative_ as we want do decrement the time
            # remaining in each timer
            delta = start_time - end_time
            _logger.debug("run_once() took %f seconds to run", -delta)
            self._adjust_timers(delta)

    def _adjust_timers(self, delta):
        _logger.debug("processing timer events")
        # create a new list of timers, dropping timers that ran out
        for timer in self._timers:
            timer.adjust(delta)
        # keep only timers that are still pending (yet to fire)
        self._timers = [timer for timer in self._timers if timer.pending]

    def _should_keep_running(self):
        retval = super()._should_keep_running() or bool(self._timers)
        _logger.debug("(timers) _should_keep_running() -> %r", retval)
        return retval

    def _get_sleep_timeout(self):
        if self._timers:
            return min([
                timer.remaining
                for timer in self._timers
                if timer.pending])
        else:
            return -1

    def _get_time(self):
        try:
            return time.monotonic()
        except NameError:
            return time.time()


class _MainLoop_ProcessManagement(_MainLoop_TimerManagement):
    """
    An in implementation of a MainLoop that supports watching processes.

    This class uses :func:`posix.waitid()` function to watch for state
    changes in children processes. It observes SIGCHLD using the
    :func:`signal.signal()` function and wakes up the main loop object
    by writing dummy data to a helper pipe created with :func:`posix.pipe()`.

    Processes are wrapped in the :class:`Process` wrapper to provide better
    API. Only child processes can be observed this way.
    """

    def __init__(self):
        super().__init__()
        self._processes = {}
        self._pipe = _Pipe(nonblock=True)
        self._pipe.read_end.on_io_possible.connect(self._drain_pipe)
        self._pipe_watched = False
        self._old_SIGCHLD_handler = signal.signal(
            signal.SIGCHLD, self._on_SIGCHLD)

    def watch_process(self, process):
        """
        Watch for activity of the specified process.

        :param process:
            A :class:`Process` object to watch

        The activity includes:
         - process exiting normally
         - process being killed by signal
         - process being suspended or resumed

        See various signals in :class:`Process` for details.
        """
        if not isinstance(process, Process):
            raise TypeError("expected Process instance")
        if not self._processes:
            self._watch_pipe()
        self._processes[process.pid] = process
        _logger.debug("watching process: %r", process)

    def remove_process_watch(self, process):
        """
        Stop watching for activity of the specified process.

        This method undoes the effects of :meth:`watch_process()`.

        :param process:
            A :class:`Process` object to stop watching
        :raises TypeError:
            If ``process`` is not an instance of :class:`Process`

        For API simplicity, it is safe to call this on a process that is
        no longer being watched. Normally processes automatically un-watch
        themselves when they die so it would make any kind of cleanup code
        cumbersome if a check was required around each call to this method.
        """
        if not isinstance(process, Process):
            raise TypeError("expected Process instance")
        try:
            del self._processes[process.pid]
        except KeyError:
            pass
        else:
            _logger.debug("no longer watching process %r", process)
            # if no more processes remain, stop watching the support pipe
            if not self._processes:
                self._unwatch_pipe()

    def close(self):
        signal.signal(signal.SIGCHLD, self._old_SIGCHLD_handler)
        if self._pipe_watched:
            self._unwatch_child_pipe()
        self._pipe.read_end.on_io_possible.disconnect(self._drain_pipe)
        self._pipe.close()
        super().close()

    def run_once(self):
        super().run_once()
        if self._processes:
            for event in self._get_waitid_events():
                self._process_waitid_event(event)

    def _watch_pipe(self):
        self.watch_descriptor(self._pipe.read_end, select.EPOLLIN)
        self._pipe_watched = True
        _logger.debug("watching for support pipe")

    def _unwatch_pipe(self):
        self.remove_descriptor_watch(self._pipe.read_end)
        self._pipe_watched = False
        _logger.debug("no longer watching for support pipe")

    def _drain_pipe(self, events):
        assert select.EPOLLIN & events
        # assert fd == self._child_pipe.read_end.fd
        # TODO: read until drained, remember it's non-blocking!
        os.read(self._pipe.read_end.fd, 1)

    def _on_SIGCHLD(self, num, frame):
        os.write(self._pipe.write_end.fd, b'\0')

    # NOTE: this is disabled because we always want to keep running
    # if there are processes and we don't need anything apart from the
    # tracking pipe that we watch if there is at least one process

    #def _should_keep_running(self):
    #    retval = super()._should_keep_running() or bool(self._processes)
    #    _logger.debug("(ProcessManagement) _should_keep_running -> %r",
    #                  retval)
    #    return retval

    def _get_waitid_events(self):
        more = True
        while more:
            try:
                _logger.debug("waitid() ...")
                result = posix.waitid(
                    posix.P_ALL, 0,
                    posix.WEXITED | posix.WSTOPPED | posix.WCONTINUED
                    | posix.WNOHANG)
                _logger.debug("waitid() -> %r", result)
                if result is None:
                    more = False
                else:
                    yield result
            except OSError as exc:
                _logger.debug("waitid() *** %r", exc)
                if exc.errno == errno.ECHILD:
                    more = False
                else:
                    raise

    def _process_waitid_event(self, event):
        _logger.debug("processing waitid event: %r", event)
        # Try to find the process in our internal mappings:
        try:
            process = self._processes[event.si_pid]
        except KeyError:
            _logger.warning("unknown process: %r", event.si_pid)
            return
        # Check if the process exited, got killed by a signal,
        # got suspended or resumed and react accordingly.
        if posix.WIFEXITED(event.si_status):
            process.on_exit(posix.WEXITSTATUS(event.si_status))
        if posix.WIFSIGNALED(event.si_status):
            process.on_death_by_signal(posix.WTERMSIG(event.si_status))
        if posix.WIFCONTINUED(event.si_status):
            process.on_resume()
        if posix.WIFSTOPPED(event.si_status):
            signal_num = posix.WSTOPSIG(event.si_status)
            if signal_num != 0:
                process.on_suspend(signal_num)
            else:
                _logger.warning("treating WSTOPSIG() == 0 as exit")
                process.on_termination()
        # If the process is considered dead remove it from children tracking.
        if process.is_terminated:
            self.remove_process_watch(process)


class MainLoop(_MainLoop_ProcessManagement):
    """
    Implementation of the main-loop concept capable of watching
    descriptors, processes and timers
    """

    def close(self):
        """
        Release all of the system resource associated with this main loop.
        """
        super().close()

    def run_once(self):
        """
        Run exactly one iteration of the loop.
        """
        super().run_once()