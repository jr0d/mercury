.. Mercury documentation master file, created by
   sphinx-quickstart on Tue Jan 10 23:25:20 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: images/project_mercury.png
   :alt: Liquid Metal
   :align: center

.. centered:: Mercury
.. centered:: *An element having the properties of liquid metal*

Welcome to Mercury's |release| documentation!
=============================================

Overview
--------
Mercury is a set of services, agents, and libraries designed for the
purpose of heterogeneous datacenter management.

Mercury provides two core facilities, a hardware inventory and an abstraction
API for firmware management, BMC configuration, RAID configuration,
OS provisioning, and secure decommissioning. Mercury has been developed
specifically for base systems management of large numbers of servers from
multiple vendors and generations, spread across multiple datacenters.

Mercury is approaching alpha status and is currently under **heavy** development.
All aspects of the project, be it code, structure, philosophy; are likely to change.

.. sidebar:: WARNING

   *Use at your own risk, without any warranty, implied or otherwise*

General Reading
---------------
:doc:`mercury_in_practice`
   Book format with Mercury

Installation
------------
For development and testing, the server and the agent can be directly installed
from pip. The agent typically runs in an a stateless environment with access to
server management utilities. For the safety of your development environment, **do
not run the agent as root**, unless you really know what you are doing.

Requirements
~~~~~~~~~~~~
Python 3.5+ for the server

Python 2.7+ for the agent

Server
~~~~~~
.. code-block:: bash

   $ pip install mercury-server

Agent
~~~~~
.. code-block:: bash

   $ pip install mercury-agent

Quick Start
-----------

*"So you want to be a millionaire?"*

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents:

