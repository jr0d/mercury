# Mercury
<i>Liquid Metal</i>


![alt tag](docs/images/project_mercury.png)

[![Build Status](https://travis-ci.org/jr0d/mercury.svg?branch=master)](https://travis-ci.org/jr0d/mercury)

# Welcome
This repository houses common libraries and the core backend services of the mercury stack. Some other mercury notable
repositories are:

* [mercury-agent](https://github.com/jr0d/mercury-agent) : agent code, RPC endpoints, inspectors, and hardware libraries
* [mercury-api](https://github.com/jr0d/mercury-api) : the frontend HTTP API
* [mercury-sdk](https://github.com/jr0d/mercury-sdk) : Python SDK for mercury and the Mercury command line interface,
    mcli


# Overview

**Mercury is a set of services, agents, and libraries designed for the purpose of managing datacenter hardware assets**

Mercury provides two core facilities, a searchable hardware inventory and an API for remotely managing devices. The latter is comes via a powerful RPC system which provides first party remote support for managing firmware, BMCs, hardware RAID controllers, and local storage. 

Mercury has been developed specifically for base systems management of large numbers of servers from multiple vendors and generations,
spread across multiple datacenters.


### Mercury Inventory
When a server boots using the [mercury agent](https://github.com/jr0d/mercury-agent), software inspectors interrogate the hardware. The gathered information is
structured into detailed objects, which are easily serialized and imported. These objects represent various attributes
of a device, such as CPU, memory, vendor asset information, network devices and link information, storage details (RAID
and onboard), and subsystem bus information (PCI and USB). Once these objects are created, they are serialized and
transmitted to the mercury inventory controller for storage. From the outside (using the mercury HTTP API) the inventory
is ephemeral and read only. It can only be updated by a Mercury Agent.

### MercuryId

MercuryId is a vendor neutral method for heuristically generating a unique value for a hardware chassis.
The Id is generated in multiple ways. In the case of OEMs that guarantee a unique product UUID in SMBIOS tables,
the mercury ID is hashed directly from that value. For ODMs and white boxes, the Id is typically a hash of all on board
interface MAC addresses.

The mercury ID should never change for a given chassis. If a device has it's RAM or CPU replace in
the rack, the value will not change. This allows mercury to correlate datacenter location information (LLDP)
to a unique device; which is a rather important feature which provides Mercury's in the rack, automated
discovery.



### Mercury Agent
The core agent that operates within an ephemeral OS running on an inventory target (device still under provider
control, ie not sold or allocated). The OS environment contains libraries and abstraction layers for the intent of
providing a common RPC interface for provisioning and decommissioning workflows. Agent capabilities expose mechanisms
for managing firmware, hardware RAID, OS Provisioning, drive sanitation, etc.

### Inspectors
These core software units provide the most precises and full featured libraries for interrogating hardware, discovering
network interfaces and neighbors (LLDP), and detecting hardware state change. Used primarily for populating the
mercury_inventory database, but also useful for standalone operation

### Supported inspectors
- bmc
- cpu
- dmi
- interfaces
- mem
- os_storage
- pci
- raid
- routes

### Async Inspectors
- lldp
- slow_scan (Interrupt based hardware interrogation)

### RPC

The agent provides an extensible python RPC interface. Exposed procedures, or capabilities, are published by the agent.
The published data includes the method name, method prototype requirements (args and kwargs), doc string, and locking 
information.

### Base capabilities

- run
- update_firmware
- update_firmware_package
- secure_erase
- zero_fill
- configure_bmc_lan
- configure_bmc_user
- press (OS Provisioning)
- kexec
- inspector
- stress
- set_cpu_frequency
- disk_benchmark
- set_boot_order

### Abstract RAID operations
*For supported controllers (LSI/PERC, HPSSA, MPTFusion)*

- create_logical_drive
- delete_logical_drive
- add_spares
- clear_configuration

### Direct capabilities

- ipmitool
- hponcfg
- conrep
- hphealth
- hpsum_update
- hpssa_create_array
- hpssa_delete_ld
- hpssa_clear_configuration
- hpssa_clear_configuration_all_controllers
- dtk_update
- omreport_health
- syscfg
- megaraid_add
- megaraid_delete
- megaraid_firmware_update

Full RPC method documentation can be viewed in the RPC section of the API documentation

### Preprocessors

Parallel execution of an identical task does not always make sense. This is especially evident when considering
the press workflow. For instance, if I happen to create a job that matches 12 active inventory records and provide a
single press configuration to the `press` method, all 12 nodes would be provisioned using the same user and
networking information. This is usually not the intended result. As such, mercury provides a preprocessor interface.


With preprocessors, press templates can be rendered using inventory data and external asset management
systems. Adding preprocessors can occur through the plugin interface. See [Preprocessor](documentation_link)
documentation for more information


This version of Mercury provides a reference implementation called `press_static_assets`. As the name suggest, it
allows the user to submit a set of static assets, referenced by mercury_id, to be used when rendering the provided
template. 

### Transport

For all backend communication, mercury uses [0mq socket API](http://zeromq.org/whitepapers:architecture) and
[MessagePack](https://github.com/msgpack/msgpack/blob/master/spec.md) for serialization . Mercury is 
designed to work in tandem with production workloads; as such, mercury’s messaging system has been 
developed to minimize impact on overall network capacity.


# Docker
## Building a local test image

A Dockerfile exist which will install the current source tree into
a docker image, along with the test suite.

To build the image use the following command

```
docker build -t local/mercury-core -f docker/mercury-core-local/Dockerfile .
```

## Starting the stack

Once the local image has been built, use the full stack compose file to
start the mercury-core services
```
docker-compose -f docker/docker-compose-fullstack.yaml -p mercury up
```

