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


RAID Abstraction
----------------
.. automodule:: mercury.hardware.raid.abstraction.api
    :members:

