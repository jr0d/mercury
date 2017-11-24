# Mercury
<i>Liquid Metal</i>


![alt tag](docs/images/project_mercury.png)

[![Build Status](https://travis-ci.org/jr0d/mercury.svg?branch=master)](https://travis-ci.org/jr0d/mercury)

# Welcome
This is the mercury project repository. Here you will find the core 
mercury source code and documentation targeted at developers.
User and System Administration documentation will be available at a 
later time.

Mercury is under heavy development at the moment and is currently in alpha status
and will remain so until the 0.5 release, at which point the software will enter it's
beta phase.


# Overview

**Mercury is a set of services, agents, and libraries designed for the 
purpose of managing datacenter hardware assets**

Mercury provides two core facilities, a searchable hardware inventory and an API for remotely managing firmware management, BMC
configuration, RAID configuration, OS provisioning, and secure decommissioning. Mercury has been developed specifically
for base systems management of large numbers of servers from multiple vendors and generations,
spread across multiple datacenters. 


The Mercury Inventory is automatically populated and provides a detailed, 
location aware view of hardware assets. Pairing the Inventory database with the 
Mercury RPC system allows for unprecedented level of operator control

## Mercury Is *Not*

* Mercury is not cloud software or an IaaS solution. Mercury is intended to extend the inventory and management
capabilities of these higher level applications. 

* Mercury is not configuration management. However, it's real time inventory 
databases can be used as back ends for many DevOPs workloads.


Mercury is the result of over 10 years of experience in the provisioning space at Rackspace, where we have built 
provisioning software for large, heterogeneous environments. 


## Mercury development tenets

- Simplicity
- Ease of Administration
- Control


### Mercury Inventory
When a server boots using the mercury agent, software inspectors interrogate the hardware. The gathered information is
structured into detailed objects, which are easily serialized and imported. These objects represent various attributes
of a device, such as CPU, memory, vendor asset information, network devices and link information, storage details (RAID
and onboard), and subsystem bus information (PCI and USB). Once these objects are created, they are serialized and
transmitted to the mercury inventory controller for storage. From the outside (using the mercury HTTP API) the inventory
is ephemeral and read only. It can only be updated by a Mercury Agent.

By design, the mercury inventory does not contain state information (allocated, provisioning, error, etc). In addition,
there will never be back references to external asset management systems such as CORE. The intent is that forward
references to devices will be made from existing and newly implemented systems. Mercury’s database will replace any
logical representations of hardware devices and act as the SoT for hardware information.

### Inventory Controller
Controller service for a free form, document oriented database. Populated by mercury agents and multi-band collectors
for the purpose of building a ubiquitous document structure that describes hardware. If it exists here, it exists on
the floor; exactly as described.

The controller provides a powerful, near native mongodb query interface. The controller is present to hook events and
provide granular authorization to inventory segments. It is not here to get in the way.

### MercuryId

MercuryId is a vendor neutral algorithm for heuristically generating a unique value that represents server identity.
The algorithm is simple:

```
If dmi.product_uuid is populated: id = 01 + sha1(dmi.product_uuid)

elseIf dmi.chassis_asset_tag and dmi.chassis_serial are not None:  id = 02 + sha1(dmi.chassis_asset_tag + dmi.chassis_serial)

else: id = 00 + sha1(onboard_mac_address0 + onboard_mac_addressN …)

```

The purpose of MercuryId is to create an indexable value for devices that will never change. The Id can easily be
re-generated via the aforementioned algorithm should it ever be lost.


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
- megaraid_create_array
- megaraid_delete_ld
- megaraid_clear_configuration
- megaraid_clear_configuration_all_controllers
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
