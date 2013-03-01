.. JobBox documentation master file, created by
   sphinx-quickstart on Wed Feb 13 11:18:39 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

JobBox
======

JobBox is a collection of tests that aim to cover all aspects of modern
computer hardware. It is intended to be used alongside with CheckBox and
PlainBox projects as a source of actual **data**.

The name *JobBox* is a wordplay that matches the naming scheme of the CheckBox
project group. The *job* part refers to CheckBox *jobs* which represent the
smallest piece of testing that can be performed. In essence, JobBox is just a
box with jobs.

Installation
^^^^^^^^^^^^

JobBox can be installed from a :abbr:`PPA (Personal Package Archive)`
(recommended) or :abbr:`pypi (python package index)` on Ubuntu Precise (12.04)
or newer.

.. code-block:: bash

    $ sudo add-apt-repository ppa:checkbox-dev/ppa && sudo apt-get update && sudo apt-get install jobbox 

Using JobBox
^^^^^^^^^^^^

JobBox is a dependency of PlainBox and CheckBox. It will be used automatically
whenever those tools are used.

Table of contents
=================

.. toctree::
   :maxdepth: 2

   jobspec.rst
   coverage.rst
   glossary.rst
   changelog.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
