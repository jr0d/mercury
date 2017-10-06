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
when compared to a monolithic application. Instead of only installing and running a single service
element, we instead install and run several components.

The first component is the mercury-common package. This package, as the name implies, contains
common libraries used by two or more discrete components. Following common, are the mercury-inventory,
mercury-log, and mercury-rpc packages.

.. note::
    The mercury-agent package depends heavily on the linux sysfs ABI and should only be installed on
    linux hosts. If you are developing on MacOS, this poses a problem. Fortunately, this problem is
    easily solved using Vagrant, Docker, or by spinning up a vanilla VM. More on this later.

Each mercury package contains a `setup.py` which we will run with the `develop` argument.


From the mercury repository root

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


Creating the Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All mercury services are configured using a YAML configuration file. Included with each source is a
sample file. The files are already ready for local development for the most part, so we only need
to copy them to a location mercury scans. By default, mercury scans the following directories:

* `.` (The current working directory)
* ~/.mercury
* /etc/mercury









References
~~~~~~~~~~

`Installing python on OSX <http://www.marinamele.com/2014/07/install-python3-on-mac-os-x-and-use-virtualenv-and-virtualenvwrapper.html>`_.