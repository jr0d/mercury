# Copyright 2015 Jared Rodriguez (jared.rodriguez@rackspace.com)
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

data = """
Smart Array P440ar in Slot 0 (Embedded)
   Bus Interface: PCI
   Slot: 0
   Serial Number: PDNLH0BRH7X32P
   Cache Serial Number: PDNLH0BRH7X32P
   RAID 6 (ADG) Status: Enabled
   Controller Status: OK
   Hardware Revision: B
   Firmware Version: 3.56
   Rebuild Priority: High
   Expand Priority: Medium
   Surface Scan Delay: 3 secs
   Surface Scan Mode: Idle
   Parallel Surface Scan Supported: Yes
   Current Parallel Surface Scan Count: 1
   Max Parallel Surface Scan Count: 16
   Queue Depth: Automatic
   Monitor and Performance Delay: 60  min
   Elevator Sort: Enabled
   Degraded Performance Optimization: Disabled
   Inconsistency Repair Policy: Disabled
   Wait for Cache Room: Disabled
   Surface Analysis Inconsistency Notification: Disabled
   Post Prompt Timeout: 15 secs
   Cache Board Present: True
   Cache Status: OK
   Cache Status Details: The current array controller had valid data stored in its battery/capacitor backed write cache the last time it was reset or was powered up.  This indicates that the system may not have been shut down gracefully.  The array controller has automatically written, or has attempted to write, this data to the drives.  This message will continue to be displayed until the next reset or power-cycle of the array controller.
   Cache Ratio: 10% Read / 90% Write
   Drive Write Cache: Disabled
   Total Cache Size: 2.0 GB
   Total Cache Memory Available: 1.8 GB
   No-Battery Write Cache: Disabled
   SSD Caching RAID5 WriteBack Enabled: True
   SSD Caching Version: 2
   Cache Backup Power Source: Batteries
   Battery/Capacitor Count: 1
   Battery/Capacitor Status: OK
   SATA NCQ Supported: True
   Spare Activation Mode: Activate on physical drive failure (default)
   Controller Temperature (C): 44
   Cache Module Temperature (C): 33
   Number of Ports: 2 Internal only
   Encryption: Disabled
   Express Local Encryption: False
   Driver Name: hpsa
   Driver Version: 3.4.4
   Driver Supports HP SSD Smart Path: True
   PCI Address (Domain:Bus:Device.Function): 0000:03:00.0
   Negotiated PCIe Data Rate: PCIe 3.0 x8 (7880 MB/s)
   Controller Mode: RAID
   Controller Mode Reboot: Not Required
   Latency Scheduler Setting: Disabled
   Current Power Mode: MaxPerformance
   Host Serial Number: TC51NR9952
   Sanitize Erase Supported: False
   Primary Boot Volume: None
   Secondary Boot Volume: None
Smart HBA H241 in Slot 4 (HBA Mode)
   Bus Interface: PCI
   Slot: 4
   Serial Number: PDNNL0ARH7E01K
   Cache Serial Number: PDNNL0ARH7E01K
   Controller Status: OK
   Hardware Revision: B
   Firmware Version: 3.56
   Controller Temperature (C): 43
   Number of Ports: 2 External only
   Driver Name: hpsa
   Driver Version: 3.4.4
   HBA Mode Enabled: True
   PCI Address (Domain:Bus:Device.Function): 0000:88:00.0
   Negotiated PCIe Data Rate: PCIe 3.0 x8 (7880 MB/s)
   Controller Mode: HBA
   Controller Mode Reboot: Not Required
   Current Power Mode: MaxPerformance
   Host Serial Number: TC51NR9952
Smart HBA H241 in Slot 5 (HBA Mode)
   Bus Interface: PCI
   Slot: 5
   Serial Number: PDNNL0ARH7A02A
   Cache Serial Number: PDNNL0ARH7A02A
   Controller Status: OK
   Hardware Revision: B
   Firmware Version: 3.56
   Controller Temperature (C): 45
   Number of Ports: 2 External only
   Driver Name: hpsa
   Driver Version: 3.4.4
   HBA Mode Enabled: True
   PCI Address (Domain:Bus:Device.Function): 0000:84:00.0
   Negotiated PCIe Data Rate: PCIe 3.0 x8 (7880 MB/s)
   Controller Mode: HBA
   Controller Mode Reboot: Not Required
   Current Power Mode: MaxPerformance
   Host Serial Number: TC51NR9952

"""

from press.layout.size import Size


def __parse_array_line(line):
    line = line.strip()

    array_info = {
        'letter': line.split()[1],
        'type': line.split()[3].strip('(,'),
        'free_space': Size(line.split(':')[1].strip().strip(')'))
    }

    return array_info


def __parse_addapter_details(details):
    adapters = []
    detail_indent = ' ' * 3
    array_details = None

    for line in details.splitlines():
        if not line:
            continue

        if line.find('Smart') == 0:
            array_details = __parse_array_line(line)
            adapters.append(array_details)
            continue

        if line[:3] == detail_indent:
            array_details
