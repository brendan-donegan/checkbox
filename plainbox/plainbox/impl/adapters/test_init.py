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
plainbox.impl.adapters.test_init
================================

Test definitions for plainbox.impl.adapters module
"""

from unittest import TestCase

from plainbox.impl.adapters import AdapterContext, adapter


class AdapterContextTests(TestCase):

    def test_smoke(self):
        summary = AdapterContext()

        @adapter
        def SyntaxError_summary(obj: SyntaxError) -> summary:
            return obj.msg

        @adapter
        def ValueError_summary(obj: ValueError) -> summary:
            return str(obj)

        self.assertEqual(summary(SyntaxError("message")), "message")
        self.assertEqual(summary(ValueError("other message")), "other message")

    def test_polymorphism(self):
        ctx = AdapterContext()

        @adapter
        def _obj(obj: object) -> ctx:
            return 1

        @adapter
        def _exception(obj: Exception) -> ctx:
            return 2

        @adapter
        def _value_error(obj: ValueError) -> ctx:
            return 3
        # The adapters work when invoked directly
        self.assertEqual(ctx(object()), 1)
        self.assertEqual(ctx(Exception()), 2)
        self.assertEqual(ctx(ValueError()), 3)
        # AdapterContexts also pick other objects of derived classes
        # str is an object so we get 1
        self.assertEqual(ctx("foo"), 1)
        # IOError is an Exception so we get 2
        self.assertEqual(ctx(IOError()), 2)
        # custom error is a ValueError so we get 3

        class CustomError(ValueError):
            pass
        self.assertEqual(ctx(CustomError()), 3)

    def test_class_list(self):
        self.assertEqual(AdapterContext().class_list, ())
        ctx = AdapterContext()

        @adapter
        def _Exception_adapter(obj: Exception) -> ctx:
            pass  # pragma: no cover

        @adapter
        def _object_adapter(obj: object) -> ctx:
            pass  # pragma: no cover
        # Unordered comparison
        self.assertCountEqual(ctx.class_list, (Exception, object))

    def test_exception_list(self):
        self.assertEqual(AdapterContext().class_list, ())
        ctx = AdapterContext()

        @adapter
        def _Exception_adapter(obj: Exception) -> ctx:
            pass  # pragma: no cover

        @adapter
        def _object_adapter(obj: object) -> ctx:
            pass  # pragma: no cover

        self.assertEqual(ctx.exception_list, (Exception,))

    def test_doc(self):
        self.assertEqual(AdapterContext("doc").__doc__, "doc")

    def test_repr(self):
        # Documentation is a part of repr()
        self.assertIn("foo", repr(AdapterContext("foo")))

    def test_no_adapter_for_type(self):
        ctx = AdapterContext()
        with self.assertRaises(TypeError) as call:
            ctx("foo")
        self.assertEqual(str(call.exception), "no adapter for <class 'str'>")

    def test_missing_obj_annotation(self):
        with self.assertRaises(TypeError) as call:
            @adapter
            def foo(obj):
                pass  # pragma: no cover
        self.assertEqual(
            str(call.exception), "obj type annotation not specified")

    def test_missing_return_annotation(self):
        with self.assertRaises(TypeError) as call:
            @adapter
            def foo(obj: object):
                pass  # pragma: no cover
        self.assertEqual(
            str(call.exception), "return type annotation not specified")

    def test_wrong_return_annotation(self):
        with self.assertRaises(TypeError) as call:
            @adapter
            def foo(obj: object) -> object:
                pass  # pragma: no cover
        self.assertEqual(
            str(call.exception),
            "return type annotation must be an AdapterContext instance")
