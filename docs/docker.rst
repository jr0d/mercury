Using Docker and Docker-Compose with Mercury
--------------------------------------------

Support for Docker and Docker Compose has been added to Mercury to support
developers deploying locally. There are a few caveats though:

* Only the Mercury RPC Workers can be scaled
* You may need to adjust the network settings for your environment
* Be careful of dynamic and static assignments.

ZeroMQ does not seem to care for the Docker Container Naming scheme; thereby
to be able to deploy using Docker and Docker-Compose you must explicitly set up
a Docker Network and control the IP addresses in order to be able to configure
the full environment. The `docker-compose.yml.template` file is setup to use
a 172.16.200.0/24 network as an example, but may need to be modified for your
local network settings.

While settings up the docker container, the dynamically assigned containers
seem to grab the IPs faster from Docker than those with static assignments.
Therefore when configuring the Docker Network push the static assignments out
to give sufficient space for any dyanmic assignments.

At present, only the Mercury RPC Workers receive dynamic assignments. However,
this may change if linking projects together via the External Network linkages
supported by Docker Compose.

Supported Docker Containers
---------------------------

The Mercury Docker functionality provides the following containers for use:

* mongodb - MongoDB
* redis - Redis
* mercury_inventory - Mercury Inventory Service
* mercury_log - Mercury Log Service
* mercury_rpc_frontend - Mercury RPC Front End Service
* mercury_rpc_backend - Mercury RPC Back End Service
* mercury_rpc_workers - Mercury RPC Workers

Configuration
-------------

Mercury providese a template `docker-compose.yml` file for use called
`docker-compose.yml.template` in the source root directory. Outside of the
network configuration it is ready to go. It can be used by doing the following:

.. code-block:: bash

	$ cp docker-compose.yml.template docker-compose.yml

.. note:: The `docker-compose.yml` file is kept as a template so that changes
	are not automatically added to the repository since local changes may
	be necessary to use the file.

Running the Docker Containers
-----------------------------

Docker Compose enables the services to be run in one of two manners:

.. code-block:: bash

	$ docker-compose up <service name>

to run specific services; or...

.. code-block:: bash

	$ docker-compose up

to run everything. The above however will keep docker in control of the
terminal it was run from though. Use the `-d` parameter to daemonize everything
so that the terminal can be used for other things:

.. code-block:: bash

	$ docker-compose up -d

When you're all done simply run the following to terminate all the containers:

.. code-block:: bash

	$ docker-compose down

Scaling Docker Workers
----------------------

By default Docker only starts one of each service. However, it might be
beneficial to tests somethings in redundancy. By default only the Mercury RPC
Workers can be scaled due to the network configuration in place.

To add additional RPC workers:

.. code-block:: bash

	$ docker-compose up --scale mercury_rpc=<worker count>

.. note:: Scaling containers can be done in separate terminals if not using
	the `-d` flag.

.. note:: The only thing preventing all the containers from being able to
	scale is the ZeroMQ DNS resolution functionality and having to specify
	explicit IP addresses for the ZeroMQ clients.

Public Interfaces
-----------------

The following containers have public network interfaces:

* mercury_log
* mercury_rpc_frontend
* mercury_inventory

The network configuration for these can be discovered at run-time via the
following command:

.. code-block:: bash

	$ docker network inspect mercury_mercury_public

.. note:: Docker Compose adds another layer in the naming of resources, thus
	while the name internally is `mercury_public` with Docker Compose the real
	name in Docker itself is `mercury_mercury_public`. The same is true of
	all other resources deployed with Docker Compose.
