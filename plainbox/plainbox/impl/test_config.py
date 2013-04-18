# This file is part of Checkbox.
#
# Copyright 2013 Canonical Ltd.
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
plainbox.impl.test_config
=========================

Test definitions for plainbox.impl.config module
"""

from unittest import TestCase

from plainbox.impl.config import Config, ConfigMetaData
from plainbox.impl.config import KindValidator
from plainbox.impl.config import Variable


class VariableTests(TestCase):

    def test_name(self):
        v1 = Variable()
        self.assertIsNone(v1.name)
        v2 = Variable('var')
        self.assertEqual(v2.name, 'var')
        v3 = Variable(name='var')
        self.assertEqual(v3.name, 'var')

    def test_section(self):
        v1 = Variable()
        self.assertEqual(v1.section, 'DEFAULT')
        v2 = Variable(section='foo')
        self.assertEqual(v2.section, 'foo')

    def test_kind(self):
        v1 = Variable(kind=bool)
        self.assertIs(v1.kind, bool)
        v2 = Variable(kind=int)
        self.assertIs(v2.kind, int)
        v3 = Variable(kind=float)
        self.assertIs(v3.kind, float)
        v4 = Variable(kind=str)
        self.assertIs(v4.kind, str)
        v5 = Variable()
        self.assertIs(v5.kind, str)
        with self.assertRaises(ValueError):
            Variable(kind=list)

    def test_validator_list(self):
        v1 = Variable()
        self.assertEqual(v1.validator_list, [KindValidator])


class ConfigTests(TestCase):

    def test_Meta_present(self):
        class TestConfig(Config):
            pass
        self.assertTrue(hasattr(TestConfig, 'Meta'))

    def test_Meta_base_cls(self):
        class TestConfig(Config):
            pass
        self.assertTrue(issubclass(TestConfig.Meta, ConfigMetaData))

        class HelperMeta:
            pass

        class TestConfigWMeta(Config):
            Meta = HelperMeta
        self.assertTrue(issubclass(TestConfigWMeta.Meta, ConfigMetaData))
        self.assertTrue(issubclass(TestConfigWMeta.Meta, HelperMeta))

    def test_Meta_variable_list(self):
        class TestConfig(Config):
            v1 = Variable()
            v2 = Variable()
        self.assertEqual(
            TestConfig.Meta.variable_list,
            [TestConfig.v1, TestConfig.v2])


class ConfigMetaDataTests(TestCase):

    def test_filename_list(self):
        self.assertEqual(ConfigMetaData.filename_list, [])

    def test_variable_list(self):
        self.assertEqual(ConfigMetaData.variable_list, [])
