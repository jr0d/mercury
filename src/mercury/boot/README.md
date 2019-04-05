# Mercury Boot Controller

This service provides a mechanism for controlling the boot state of iPXE clients.

# How it works
When an iPXE client sends an HTTP request to the /boot it receives a 'discovery' script

```text
#!ipxe

echo MERCURY BOOT DISCOVERY
chain {{ mercury_boot_url }}/boot/discover/${netX/mac} || shell
```

This instructs the ipxe client to hit the /boot/discover endpoint with the mac address of the
interface that made the first request. This is typically the interface which was previously
configured via a DHCP request. The boot controller will correlate the provided mac address
with a mercury inventory record. The inventory record contains the current boot 'state' of the 
device.

## States

* **agent**: boots a preboot environment containing the mercury agent
* **rescue**: boots a preboot containing an internet accessible rescue environment
* **local**: boots the device from local storage

## Custom scripts
The inventory may also store custom iPXE scripts. For information on writing ipxe scripts see
the ipxe documentation.

<< Provide examples here >> 