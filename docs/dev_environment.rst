Building a Development Environment for Mercury
---------------------------------------

Here we will discuss setting up a development environment. We will cover steps
and strategies for deploying natively on linux, running the agent in vagrant on OSX,
and setting up a virtual network and virtual machine targets to test end to end provisioning.


Get The Code
~~~~~~~~~~~~

Like most open source projects, the mercury source code is available on github. Let's
start by cloning the repository.

.. code-block:: bash

    $ git clone https://github.com/jr0d/mercury.git

This will create a directory called mercury in your current working directory.

Also, we will probably want to interact with mercury using the HTTP API, so be sure to clone this repository as
well:

.. code-block:: bash

    $ git clone https://github.com/jr0d/mercury_api.git


Install Python 3.6 and virtualenv
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This process will very per your distribution. It is here for the uninitiated, if you already
have a working python3.6 development environment, you can skip to the mercury install section.

.. warning::

    If you intend to skip the guided python-3.6 install process, ensure that gcc, gcc-c++, automake,
    autoconf, and python development headers are installed. They are require to build zeromq during
    the merucry install process

Enterprise Linux 7 / CentOS 7
_____________________________

.. code-block:: bash

    yum install -y https://mirror.rackspace.com/ius/stable/CentOS/7/x86_64/ius-release-1.0-15.ius.centos7.noarch.rpm && \
    yum install -y gcc gcc-c++ automake autoconf python36u python36u-devel python36u-pip && \
    pip3.6 install virtualenv

Ubuntu 16.04
______

For python 3.6 (preferred)

.. code-block:: bash

    apt-get update && \
    apt-get -y install software-properties-common && \
    add-apt-repository -y ppa:jonathonf/python-3.6 && \
    apt-get update && \
    apt-get -y install gcc g++ automake python3.6 python3.6-dev wget && \
    wget https://bootstrap.pypa.io/get-pip.py -O - | python3.6 && \
    pip3.6 install virtualenv

For python3.5, just install the python3.5-dev and python3.5-pip packages. Then:

.. code-block:: bash

    pip3 install virtualenv


OSX
____

I do not have an OSX machine to test this on, but I believe the following `should` work

.. code-block:: bash

    brew install python3
    pip install virtualenv


Installing service dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mercury utilizes mongodb for persistent storage and redis for distributed queuing. Install
both of these services from your distributions package management repositories. Ensure that
both mongodb and redis are running locally before proceeding.


Create a virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ mkdir ~/.virtualenvs
   $ virtualenv -p`which python3.6` ~/.virtualenvs/mercury


Now activate the virtual environment.


.. code-block:: bash

   $ source ~/.virtualenvs/mercury/bin/activate


.. note::

   You will need to activate the virtual environment whenever you are running a mercury service.
   To make virtualenv management easier, consider using
   `virtualenvwrapper <http://virtualenvwrapper.readthedocs.io/en/latest/install.html>`_ or
   `pyvenv <https://docs.python.org/3/library/venv.html>`_.


Installing Mercury Services
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mercury implements a micro-services architecture. This allows us to deploy and scale components
independently. Unfortunately, such an architecture slightly complicates the development process
when compared to a monolithic application. Instead of installing and running a single service
element, we must install and run several components.

The first component is the mercury-common package. This package, as the name implies, contains
common libraries used by two or more discrete components. Following common, are the mercury-inventory,
mercury-log, and mercury-rpc packages.

.. note::
    The mercury-agent package depends heavily on the linux sysfs ABI and should only be installed on
    linux hosts. If you are developing on MacOS, this poses a problem. Fortunately, this problem is
    easily solved using Vagrant, Docker (untested), or by spinning up a vanilla VM. More on this
    later.

Each mercury package contains a *setup.py* which we will run with the *develop* argument.


From the mercury repository root:

.. code-block:: bash

    pushd src/mercury-common && \
    python setup.py develop && \
    popd && \
    pushd src/mercury-inventory && \
    python setup.py develop && \
    popd && \
    pushd src/mercury-rpc && \
    python setup.py develop && \
    popd && \
    pushd src/mercury-log && \
    python setup.py develop && \
    popd


If you are installing the HTTP API, make sure to install that too

.. code-block:: bash
    cd mercury-api && python setup.py develop


Creating the Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All mercury services are configured using a YAML configuration file. Included with each source is a
sample file. The files are already ready for local development for the most part, so we only need
to copy them to a location mercury scans. By default, mercury scans the following directories:

* . (The current working directory)
* ~/.mercury
* /etc/mercury

.. note::

    Once the **find_configuration()** function *finds* the configuration file it is looking for,
    the loop breaks. If you happen to have a configuration file in your local directory and in /etc/mercury,
    the configuration in /etc/mercury will be ignored.

For easy use, we will be populating our configuration files in our home directory, **~/.mercury**. Keep in mind,
Mercury is under heavy development, so watch for changes to the configuration file samples when pulling master; making
sure to update your local copies when necessary.

From the mercury repository root:

.. code-block:: bash

    mkdir -p ~/.mercury && \
    for _package in mercury-inventory mercury-rpc mercury-log; \
    do cp src/${_package}/${_package}-sample.yaml ~/.mercury/${_package}.yaml; done


Running the Services
~~~~~~~~~~~~~~~~~~~~

I am currently designing the service launcher and CLI for the inventory and backend components. Once implemented, this
process, which requires us to launch each service directly by calling *x/server.py*; **will go away**. For now, this
is what we have.

The services we need to launch are located in the mercury-inventory, mercury-rpc, and mercury-log packages. In addition
to these, we probably want to start the API bottle service as well.

* mercury-inventory

  * Inventory Service | *python src/mercury-inventory/mercury/inventory/server.py*

* mercury-rpc

  * Front End ZeroMQ service | *python src/mercury-rpc/mercury/rpc/frontend/frontend.py*
  * Back End ZeroMQ service  | *python src/mercury-rpc/mercury/rpc/backend/backend.py*
  * Workers service          | *python src/mercury-rpc/mercury/rpc/workers/worker.py*

* mercury-log

  * Logging service | *python src/mercury-log/log_service/server.py*

* mercury-api

  * Bottle API service | *python mercury-api/mercury_api/frontend.py*

With an IDE, such as pycharm, I typically create a profile for each service launcher. How you start
these services is up to you. There is a script provided in the scripts directory which will launch
all services in separate tmux windows ( with the exception of the mercury_api, which exists in
another repository ).

Once these services are running, we are ready to connect an agent to the backend.

Running the Agent
~~~~~~~~~~~~~~~~~

On linux, running the agent is as simple as running any other service.




References
~~~~~~~~~~

`Installing python on OSX <http://www.marinamele.com/2014/07/install-python3-on-mac-os-x-and-use-virtualenv-and-virtualenvwrapper.html>`_.