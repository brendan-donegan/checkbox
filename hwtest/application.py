import os
import logging

from logging import StreamHandler, FileHandler, Formatter
from optparse import OptionParser

from hwtest.contrib import bpickle_dbus
from hwtest.contrib.persist import Persist

from hwtest import VERSION

from hwtest.plugin import PluginManager
from hwtest.question import parse_file
from hwtest.reactor import Reactor
from hwtest.test import Test, TestManager
from hwtest.constants import SHARE_DIR
from hwtest.report import Report


class Application(object):

    def __init__(self, reactor, questions, data_path,
                 log_handlers=None, log_level=None):

        # Logging setup
        format = ("%(asctime)s %(levelname)-8s %(message)s")
        if log_handlers:
            for handler in log_handlers:
                handler.setFormatter(Formatter(format))
                logging.getLogger().addHandler(handler)
            if log_level:
                logging.getLogger().setLevel(log_level)
        elif not logging.getLogger().handlers:
            logging.disable(logging.CRITICAL)

        # Reactor setup
        if reactor is None:
            reactor = Reactor()
        self.reactor = reactor

        # Persist setup
        persist_filename = os.path.join(data_path, "data.bpickle")
        self.persist = self.get_persist(persist_filename)

        # Report setup
        self.report = Report()

        # Test manager setup
        self.test_manager = TestManager()

        # Questions
        questions = parse_file(questions)
        tests = [Test(**q) for q in questions]
        for test in tests:
            self.test_manager.add(test)

        # Plugin manager setup
        self.plugin_manager = PluginManager(self.reactor, self.report,
            self.persist, persist_filename)
        self.plugin_manager.load(os.path.join(os.path.dirname(__file__), 'plugins'))

        # Test plugins
        for test in tests:
            self.plugin_manager.add(test)

    def get_persist(self, persist_filename):
        persist = Persist()

        if os.path.exists(persist_filename):
            persist.load(persist_filename)
        persist.save(persist_filename)
        return persist

    def get_tests(self):
        return self.test_manager.get_iterator()

    def run(self):
        try:
            bpickle_dbus.install()
            self.reactor.run()
            bpickle_dbus.uninstall()
        except:
            logging.exception("Error running reactor.")
            bpickle_dbus.uninstall()
            raise


class ApplicationManager(object):

    application_factory = Application

    def create(self, options):
        log_level = logging.getLevelName(options.log_level.upper())
        log_handlers = []
        log_handlers.append(StreamHandler())
        if options.log:
            log_filename = options.log
            log_handlers.append(FileHandler(log_filename))

        reactor = Reactor()

        data_path = os.path.expanduser(options.data_path)

        return self.application_factory(reactor, questions=options.questions,
            data_path=data_path, log_handlers=log_handlers,
            log_level=log_level)
