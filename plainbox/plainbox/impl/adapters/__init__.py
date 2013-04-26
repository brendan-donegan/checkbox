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
:mod:`plainbox.impl.adapters` -- adapter class
==============================================

.. warning::

    THIS MODULE DOES NOT HAVE A STABLE PUBLIC API
"""


class AdapterContext:
    """
    Context class for adapting instances of specific classes into arbitrary
    values as defined by helper functions, one for each type that should be
    adapted. The actual adapters are added using the :func:`adapter()`
    decorator.
    """

    def __init__(self, doc=None):
        """
        Initialize a new AdapterContext
        """
        self._adapter_map = {}
        if doc is not None:
            self.__doc__ = doc

    def __repr__(self):
        return "<AdapterContext doc:{0!r}>".format(self.__doc__)

    @property
    def class_list(self):
        """
        list of classes that have adapter functions in this context.
        """
        return tuple(self._adapter_map.keys())

    @property
    def exception_list(self):
        """
        list of exceptions that have adapter functions in this context.

        This property is useful in constructing try/catch exceptions. It can be
        used instead of the type of exception to catch. It will catch all of
        the exceptions of the types that have registered adapters.
        """
        return tuple([
            cls for cls in self.class_list
            if issubclass(cls, BaseException)])

    def _register(self, from_cls, func):
        """
        Internal method called by :func:`adapter()` decorator.
        """
        self._adapter_map[from_cls] = func

    def __call__(self, obj):
        """
        Adapt object according to known rules

        :returns:
            whatever was returned by the most specialized adapter method

        :raises TypeError:
            if there is no adapter for the type of `obj`
        """
        cls_list = type(obj).__mro__
        for cls in cls_list:
            if cls in self._adapter_map:
                return self._adapter_map[cls](obj)
        raise TypeError("no adapter for {0}".format(cls_list[0]))


def adapter(func):
    """
    Decorator for adapter functions.

    See the module documentation for usage instructions.
    """
    if 'obj' not in func.__annotations__:
        raise TypeError("obj type annotation not specified")
    from_cls = func.__annotations__['obj']
    if 'return' not in func.__annotations__:
        raise TypeError("return type annotation not specified")
    to_ctx = func.__annotations__['return']
    if not isinstance(to_ctx, AdapterContext):
        raise TypeError(
            "return type annotation must be an AdapterContext instance")
    to_ctx._register(from_cls, func)
    return func
