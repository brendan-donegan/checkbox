Type Adapters
=============

Adapter context is small utility class that allows for decentralized conversion
of values of particular types (e.g. particular exceptions) into other values
that is appropriate to a particular use case.

Adapter Context Objects
-----------------------

Different adapter context objects can be used to convert the same type instance
into different values. For example the same exception can be adapted into a
short text message, a log record, a piece of data that is displayed in a
graphical application::

    >>> from plainbox.impl.adapters import AdapterContext

All instances of the :class:`plainbox.impl.adapters.AdapterContext` class can
used as function for transforming objects of particular classes into other
objects. For example here the ``summary`` object will be used as a means to
summarize errors::

    >>> summary = AdapterContext("summary of something")

The @adapter decorator
----------------------

Particular adapters can be added to a context using a simple decorator. The
decorator is used the same way in all cases, the decorated function must take
one argument called 'obj' and needs to have annotations on both that argument
and the return type. The annotation of the ``obj`` can be any type subclass
(any class or built-in type). The annotation of the return value must be an
``AdapterContext`` instance::

    >>> @adapter
    ... def _SyntaxError_adapter(obj:SyntaxError) -> summary:
    ...     return "{filename}:{lineno}: {msg}".format(
    ...         filename=error.filename, lineno=error.lineno, msg=error.msg)

All ``AdapterContext`` instances are callable. For example, using the
``summary`` object, we can now convert any :class:`SyntaxError` instance to a
short summary message::

    >>> summary(SyntaxError(
    ...     "expected variable", ('job.txt', 12, 156, "something")))
    "job.txt:12: expected variable"

This mechanism is polymorphic. An adapter on base type will adapt derived types
as well. An adapter on more specialized derivation overrides adapters for the
more basic derivation.

This adapter shows how to summarize any object::

    >>> @adapter
    ... def _object_adapter(obj:object) -> summary:
    ...     return "summary of {}".format(obj)

Using that generic adapter we can now summarize anything. Here a instance of
``int`` type is passed and summarized::

    >>> summary(10)
    "summary of 10"

Here a instance of ``str`` type is passed and summarized::

    >>> summary("foo")
    "summary of foo"

Using AdapterContext with exceptions
------------------------------------

The initial use case for the adapter mechanism was to allow to create
appropriate error messages for various unrelated exception classes in a way
which the code can be easily tested and reused. It is also designed in a way so
that the code can be easily spread in separate modules. The only central point
is the actual instance of ``AdapterContext``, that has to be imported in each
module that wants to add adapters to it.

There is one auxiliary property that is useful in this use case
:attr:`plainbox.impl.adapters.AdapterContext.exception_list`. This property
returns a list of all types that inherit from :class:`BaseException`. It can be
used instead of actual exception names in a ``try:``/``except:`` statement.

The following example shows how arbitrary exceptions can now be handled and
displayed using one adapter context. Realistic example would use multiple
adapters to create appropriate error messages for each actual exception that
may happen::

    >>> @adapter
    ... def _Exception_summary(obj:Exception) -> summary
    ...     return str(obj)


    >>> try:
    ...     raise ValueError("example")
    ... except summary.exception_list as exc:
    ...     print(summary(exc))
    summary of 'example'
