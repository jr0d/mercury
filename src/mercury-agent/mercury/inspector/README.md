# mercury-inspector
```
/home/jared/.virtualenvs/zmq/bin/python /home/jared/git/mercury/mercury-inspector/mercury_inspector/collect.py
DEBUG:mercury_inspector.inspectors.inspector:Running inspector: cpu
DEBUG:mercury_inspector.inspectors.inspector:Running inspector: dmi
DEBUG:mercury_inspector.lib.sysfs:Problem reading sysfs file /sys/class/dmi/id/product_uuid [[Errno 13] Permission denied: '/sys/class/dmi/id/product_uuid']
DEBUG:mercury_inspector.lib.sysfs:Problem reading sysfs file /sys/class/dmi/id/chassis_serial [[Errno 13] Permission denied: '/sys/class/dmi/id/chassis_serial']
DEBUG:mercury_inspector.lib.sysfs:Problem reading sysfs file /sys/class/dmi/id/product_serial [[Errno 13] Permission denied: '/sys/class/dmi/id/product_serial']
DEBUG:mercury_inspector.lib.sysfs:Problem reading sysfs file /sys/class/dmi/id/board_serial [[Errno 13] Permission denied: '/sys/class/dmi/id/board_serial']
DEBUG:mercury_inspector.inspectors.inspector:Running inspector: interfaces
DEBUG:mercury_inspector.lib.sysfs:Problem reading sysfs file /sys/class/net/wlp2s0/carrier [[Errno 22] Invalid argument]
DEBUG:mercury_inspector.lib.sysfs:Problem reading sysfs file /sys/class/net/wlp2s0/duplex [[Errno 22] Invalid argument]
DEBUG:mercury_inspector.lib.sysfs:Problem reading sysfs file /sys/class/net/wlp2s0/speed [[Errno 22] Invalid argument]
DEBUG:mercury_inspector.inspectors.inspector:Running inspector: os_storage
DEBUG:mercury_inspector.inspectors.inspector:Running inspector: pci
DEBUG:mercury_inspector.lib.mercury_id:Generating mercury ID using all interfaces
{'cpu': {'cpu0': {'cache_alignment': 64,
                  'cache_size': '6144 KB',
                  'cores': 4,
                  'flags': ['fpu',
                            'vme',
                            'de',
                            'pse',
                            'tsc',
                            'msr',
                            'pae',
                            'mce',
                            'cx8',
                            'apic',
                            'sep',
                            'mtrr',
                            'pge',
                            'mca',
                            'cmov',
                            'pat',
                            'pse36',
                            'clflush',
                            'dts',
                            'acpi',
                            'mmx',
                            'fxsr',
                            'sse',
                            'sse2',
                            'ss',
                            'ht',
                            'tm',
                            'pbe',
                            'syscall',
                            'nx',
                            'pdpe1gb',
                            'rdtscp',
                            'lm',
                            'constant_tsc',
                            'arch_perfmon',
                            'pebs',
                            'bts',
                            'rep_good',
                            'nopl',
                            'xtopology',
                            'nonstop_tsc',
                            'aperfmperf',
                            'eagerfpu',
                            'pni',
                            'pclmulqdq',
                            'dtes64',
                            'monitor',
                            'ds_cpl',
                            'vmx',
                            'smx',
                            'est',
                            'tm2',
                            'ssse3',
                            'fma',
                            'cx16',
                            'xtpr',
                            'pdcm',
                            'pcid',
                            'sse4_1',
                            'sse4_2',
                            'x2apic',
                            'movbe',
                            'popcnt',
                            'tsc_deadline_timer',
                            'aes',
                            'xsave',
                            'avx',
                            'f16c',
                            'rdrand',
                            'lahf_lm',
                            'abm',
                            'ida',
                            'arat',
                            'epb',
                            'pln',
                            'pts',
                            'dtherm',
                            'tpr_shadow',
                            'vnmi',
                            'flexpriority',
                            'ept',
                            'vpid',
                            'fsgsbase',
                            'tsc_adjust',
                            'bmi1',
                            'hle',
                            'avx2',
                            'smep',
                            'bmi2',
                            'erms',
                            'invpcid',
                            'rtm',
                            'xsaveopt'],
                  'frequency': {'bogomips': 4589.5,
                                'cpufreq_enabled': True,
                                'current': 3258363.0,
                                'max': 3500000.0,
                                'min': 800000.0,
                                'model_name': 'Intel(R) Core(TM) i7-4850HQ CPU @ 2.30GHz'},
                  'model_name': 'Intel(R) Core(TM) i7-4850HQ CPU @ 2.30GHz',
                  'physical_id': 0,
                  'threads': 8}},
 'dmi': {'bios_date': '06/05/2015',
         'bios_vendor': 'Apple Inc.',
         'bios_version': 'MBP112.88Z.0138.B15.1506050548',
         'board_asset_tag': 'Base Board Asset Tag#',
         'board_name': 'Mac-3CBD00234E554E41',
         'board_serial': '',
         'board_vendor': 'Apple Inc.',
         'board_version': 'MacBookPro11,2',
         'chassis_asset_tag': '',
         'chassis_serial': '',
         'chassis_type': '10',
         'chassis_vendor': 'Apple Inc.',
         'chassis_version': 'Mac-3CBD00234E554E41',
         'modalias': 'dmi:bvnAppleInc.:bvrMBP112.88Z.0138.B15.1506050548:bd06/05/2015:svnAppleInc.:pnMacBookPro11,2:pvr1.0:rvnAppleInc.:rnMac-3CBD00234E554E41:rvrMacBookPro11,2:cvnAppleInc.:ct10:cvrMac-3CBD00234E554E41:',
         'product_name': 'MacBookPro11,2',
         'product_serial': '',
         'product_uuid': '',
         'product_version': '1.0',
         'sys_vendor': 'Apple Inc.',
         'uevent': 'MODALIAS=dmi:bvnAppleInc.:bvrMBP112.88Z.0138.B15.1506050548:bd06/05/2015:svnAppleInc.:pnMacBookPro11,2:pvr1.0:rvnAppleInc.:rnMac-3CBD00234E554E41:rvrMacBookPro11,2:cvnAppleInc.:ct10:cvrMac-3CBD00234E554E41:'},
 'interfaces': [{'address': '68:5b:35:ab:ab:89',
                 'address_info': [{'addr': '10.66.6.31',
                                   'broadcast': '10.66.7.255',
                                   'netmask': '255.255.252.0'}],
                 'address_info_v6': [{'addr': 'fe80::42bf:2276:5b48:b360%ens9',
                                      'netmask': 'ffff:ffff:ffff:ffff::'}],
                 'carrier': True,
                 'dev_port': '0',
                 'devname': 'ens9',
                 'driver': u'tg3',
                 'duplex': 'full',
                 'model_name': u'NetXtreme BCM57762 Gigabit Ethernet PCIe',
                 'pci_class': u'20000',
                 'pci_id': u'14E4:1682',
                 'pci_slot': u'0000:0a:00.0',
                 'pci_subsystem_id': u'106B:00F6',
                 'predictable_names': {'biosdevname': None,
                                       'systemd_mac': u'enx685b35abab89',
                                       'systemd_onboard': None,
                                       'systemd_slot': u'ens9',
                                       'systemd_udev': u'enp10s0'},
                 'speed': '1000',
                 'vendor_name': u'Broadcom Corporation'},
                {'address': '3c:15:c2:dc:db:98',
                 'address_info': None,
                 'address_info_v6': None,
                 'carrier': False,
                 'dev_port': '0',
                 'devname': 'wlp2s0',
                 'driver': u'wl',
                 'duplex': '',
                 'model_name': u'BCM4360 802.11ac Wireless Network Adapter',
                 'pci_class': u'28000',
                 'pci_id': u'14E4:43A0',
                 'pci_slot': u'0000:02:00.0',
                 'pci_subsystem_id': u'106B:0134',
                 'predictable_names': {'biosdevname': None,
                                       'systemd_mac': u'wlx3c15c2dcdb98',
                                       'systemd_onboard': None,
                                       'systemd_slot': None,
                                       'systemd_udev': u'wlp2s0'},
                 'speed': '',
                 'vendor_name': u'Broadcom Corporation'}],
 'mercury_id': '00b8106fc4eef2a860ba5491453e01112d54039f21',
 'os_storage': {u'/dev/sda': {u'DEVLINKS': u'/dev/disk/by-id/ata-APPLE_SSD_SM0256F_S1K4NYCF448118 /dev/disk/by-path/pci-0000:04:00.0-ata-1 /dev/disk/by-id/wwn-0x5002538655584d30',
                              u'DEVNAME': u'/dev/sda',
                              u'DEVPATH': u'/devices/pci0000:00/0000:00:1c.4/0000:04:00.0/ata1/host0/target0:0:0/0:0:0:0/block/sda',
                              u'DEVTYPE': u'disk',
                              u'ID_ATA': u'1',
                              u'ID_ATA_DOWNLOAD_MICROCODE': u'1',
                              u'ID_ATA_FEATURE_SET_AAM': u'1',
                              u'ID_ATA_FEATURE_SET_AAM_CURRENT_VALUE': u'0',
                              u'ID_ATA_FEATURE_SET_AAM_ENABLED': u'0',
                              u'ID_ATA_FEATURE_SET_AAM_VENDOR_RECOMMENDED_VALUE': u'128',
                              u'ID_ATA_FEATURE_SET_HPA': u'1',
                              u'ID_ATA_FEATURE_SET_HPA_ENABLED': u'1',
                              u'ID_ATA_FEATURE_SET_PM': u'1',
                              u'ID_ATA_FEATURE_SET_PM_ENABLED': u'1',
                              u'ID_ATA_FEATURE_SET_SECURITY': u'1',
                              u'ID_ATA_FEATURE_SET_SECURITY_ENABLED': u'0',
                              u'ID_ATA_FEATURE_SET_SECURITY_ENHANCED_ERASE_UNIT_MIN': u'32',
                              u'ID_ATA_FEATURE_SET_SECURITY_ERASE_UNIT_MIN': u'6',
                              u'ID_ATA_FEATURE_SET_SECURITY_FROZEN': u'1',
                              u'ID_ATA_FEATURE_SET_SMART': u'1',
                              u'ID_ATA_FEATURE_SET_SMART_ENABLED': u'1',
                              u'ID_ATA_ROTATION_RATE_RPM': u'0',
                              u'ID_ATA_SATA': u'1',
                              u'ID_ATA_SATA_SIGNAL_RATE_GEN1': u'1',
                              u'ID_ATA_SATA_SIGNAL_RATE_GEN2': u'1',
                              u'ID_ATA_WRITE_CACHE': u'1',
                              u'ID_ATA_WRITE_CACHE_ENABLED': u'1',
                              u'ID_BUS': u'ata',
                              u'ID_MODEL': u'APPLE_SSD_SM0256F',
                              u'ID_MODEL_ENC': u'APPLE\\x20SSD\\x20SM0256F\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20',
                              u'ID_PART_TABLE_TYPE': u'gpt',
                              u'ID_PART_TABLE_UUID': u'3150997a-e9b4-4378-91c2-5c61df24f430',
                              u'ID_PATH': u'pci-0000:04:00.0-ata-1',
                              u'ID_PATH_TAG': u'pci-0000_04_00_0-ata-1',
                              u'ID_REVISION': u'UXM2JA1Q',
                              u'ID_SERIAL': u'APPLE_SSD_SM0256F_S1K4NYCF448118',
                              u'ID_SERIAL_SHORT': u'S1K4NYCF448118',
                              u'ID_TYPE': u'disk',
                              u'ID_WWN': u'0x5002538655584d30',
                              u'ID_WWN_WITH_EXTENSION': u'0x5002538655584d30',
                              u'MAJOR': u'8',
                              u'MINOR': u'0',
                              u'SUBSYSTEM': u'block',
                              u'TAGS': u':systemd:',
                              u'UDISKS_ATA_SMART_IS_AVAILABLE': u'1',
                              u'UDISKS_PARTITION_TABLE': u'1',
                              u'UDISKS_PARTITION_TABLE_COUNT': u'6',
                              u'UDISKS_PARTITION_TABLE_SCHEME': u'gpt',
                              u'UDISKS_PRESENTATION_NOPOLICY': u'0',
                              u'USEC_INITIALIZED': u'2138917'},
                u'/dev/sdb': {u'DEVLINKS': u'/dev/disk/by-id/usb-APPLE_SD_Card_Reader_000000000820-0:0 /dev/disk/by-path/pci-0000:00:14.0-usb-0:4:1.0-scsi-0:0:0:0',
                              u'DEVNAME': u'/dev/sdb',
                              u'DEVPATH': u'/devices/pci0000:00/0000:00:14.0/usb2/2-4/2-4:1.0/host1/target1:0:0/1:0:0:0/block/sdb',
                              u'DEVTYPE': u'disk',
                              u'ID_BUS': u'usb',
                              u'ID_INSTANCE': u'0:0',
                              u'ID_MODEL': u'SD_Card_Reader',
                              u'ID_MODEL_ENC': u'SD\\x20Card\\x20Reader\\x20\\x20',
                              u'ID_MODEL_ID': u'8406',
                              u'ID_PATH': u'pci-0000:00:14.0-usb-0:4:1.0-scsi-0:0:0:0',
                              u'ID_PATH_TAG': u'pci-0000_00_14_0-usb-0_4_1_0-scsi-0_0_0_0',
                              u'ID_REVISION': u'3.00',
                              u'ID_SERIAL': u'APPLE_SD_Card_Reader_000000000820-0:0',
                              u'ID_SERIAL_SHORT': u'000000000820',
                              u'ID_TYPE': u'disk',
                              u'ID_USB_DRIVER': u'usb-storage',
                              u'ID_USB_INTERFACES': u':080650:',
                              u'ID_USB_INTERFACE_NUM': u'00',
                              u'ID_VENDOR': u'APPLE',
                              u'ID_VENDOR_ENC': u'APPLE\\x20\\x20\\x20',
                              u'ID_VENDOR_ID': u'05ac',
                              u'MAJOR': u'8',
                              u'MINOR': u'16',
                              u'SUBSYSTEM': u'block',
                              u'TAGS': u':systemd:',
                              u'UDISKS_PRESENTATION_NOPOLICY': u'0',
                              u'USEC_INITIALIZED': u'2136454'}},
 'pci': {'components': [{'class_id': '0600',
                         'class_name': 'Host bridge',
                         'device_id': '0d04',
                         'device_name': 'Crystal Well DRAM Controller',
                         'revision': '08',
                         'sdevice_id': '012e',
                         'sdevice_name': 'Device',
                         'slot': '00:00.0',
                         'svendor_id': '106b',
                         'svendor_name': 'Apple Inc.',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0604',
                         'class_name': 'PCI bridge',
                         'device_id': '0d01',
                         'device_name': 'Crystal Well PCI Express x16 Controller',
                         'driver': 'pcieport',
                         'revision': '08',
                         'slot': '00:01.0',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0300',
                         'class_name': 'VGA compatible controller',
                         'device_id': '0d26',
                         'device_name': 'Crystal Well Integrated Graphics Controller',
                         'driver': 'i915',
                         'revision': '08',
                         'sdevice_id': '012e',
                         'sdevice_name': 'Device',
                         'slot': '00:02.0',
                         'svendor_id': '106b',
                         'svendor_name': 'Apple Inc.',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0403',
                         'class_name': 'Audio device',
                         'device_id': '0d0c',
                         'device_name': 'Crystal Well HD Audio Controller',
                         'driver': 'snd_hda_intel',
                         'revision': '08',
                         'sdevice_id': '012e',
                         'sdevice_name': 'Device',
                         'slot': '00:03.0',
                         'svendor_id': '106b',
                         'svendor_name': 'Apple Inc.',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0c03',
                         'class_name': 'USB controller',
                         'device_id': '8c31',
                         'device_name': '8 Series/C220 Series Chipset Family USB xHCI',
                         'driver': 'xhci_hcd',
                         'progif': '30',
                         'revision': '05',
                         'sdevice_id': '7270',
                         'sdevice_name': 'Device',
                         'slot': '00:14.0',
                         'svendor_id': '8086',
                         'svendor_name': 'Intel Corporation',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0780',
                         'class_name': 'Communication controller',
                         'device_id': '8c3a',
                         'device_name': '8 Series/C220 Series Chipset Family MEI Controller #1',
                         'driver': 'mei_me',
                         'revision': '04',
                         'sdevice_id': '7270',
                         'sdevice_name': 'Device',
                         'slot': '00:16.0',
                         'svendor_id': '8086',
                         'svendor_name': 'Intel Corporation',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0403',
                         'class_name': 'Audio device',
                         'device_id': '8c20',
                         'device_name': '8 Series/C220 Series Chipset High Definition Audio Controller',
                         'driver': 'snd_hda_intel',
                         'revision': '05',
                         'sdevice_id': '7270',
                         'sdevice_name': 'Device',
                         'slot': '00:1b.0',
                         'svendor_id': '8086',
                         'svendor_name': 'Intel Corporation',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0604',
                         'class_name': 'PCI bridge',
                         'device_id': '8c10',
                         'device_name': '8 Series/C220 Series Chipset Family PCI Express Root Port #1',
                         'driver': 'pcieport',
                         'revision': 'd5',
                         'slot': '00:1c.0',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0604',
                         'class_name': 'PCI bridge',
                         'device_id': '8c14',
                         'device_name': '8 Series/C220 Series Chipset Family PCI Express Root Port #3',
                         'driver': 'pcieport',
                         'revision': 'd5',
                         'slot': '00:1c.2',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0604',
                         'class_name': 'PCI bridge',
                         'device_id': '8c16',
                         'device_name': '8 Series/C220 Series Chipset Family PCI Express Root Port #4',
                         'driver': 'pcieport',
                         'revision': 'd5',
                         'slot': '00:1c.3',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0604',
                         'class_name': 'PCI bridge',
                         'device_id': '8c18',
                         'device_name': '8 Series/C220 Series Chipset Family PCI Express Root Port #5',
                         'driver': 'pcieport',
                         'revision': 'd5',
                         'slot': '00:1c.4',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0601',
                         'class_name': 'ISA bridge',
                         'device_id': '8c4b',
                         'device_name': 'HM87 Express LPC Controller',
                         'driver': 'lpc_ich',
                         'revision': '05',
                         'sdevice_id': '7270',
                         'sdevice_name': 'Device',
                         'slot': '00:1f.0',
                         'svendor_id': '8086',
                         'svendor_name': 'Intel Corporation',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0c05',
                         'class_name': 'SMBus',
                         'device_id': '8c22',
                         'device_name': '8 Series/C220 Series Chipset Family SMBus Controller',
                         'revision': '05',
                         'sdevice_id': '7270',
                         'sdevice_name': 'Device',
                         'slot': '00:1f.3',
                         'svendor_id': '8086',
                         'svendor_name': 'Intel Corporation',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0280',
                         'class_name': 'Network controller',
                         'device_id': '43a0',
                         'device_name': 'BCM4360 802.11ac Wireless Network Adapter',
                         'driver': 'wl',
                         'revision': '03',
                         'sdevice_id': '0134',
                         'sdevice_name': 'Device',
                         'slot': '02:00.0',
                         'svendor_id': '106b',
                         'svendor_name': 'Apple Inc.',
                         'vendor_id': '14e4',
                         'vendor_name': 'Broadcom Corporation'},
                        {'class_id': '0480',
                         'class_name': 'Multimedia controller',
                         'device_id': '1570',
                         'device_name': '720p FaceTime HD Camera',
                         'driver': 'bdc-pci',
                         'sdevice_id': '1570',
                         'sdevice_name': '720p FaceTime HD Camera',
                         'slot': '03:00.0',
                         'svendor_id': '14e4',
                         'svendor_name': 'Broadcom Corporation',
                         'vendor_id': '14e4',
                         'vendor_name': 'Broadcom Corporation'},
                        {'class_id': '0106',
                         'class_name': 'SATA controller',
                         'device_id': '1600',
                         'device_name': 'Apple PCIe SSD',
                         'driver': 'ahci',
                         'progif': '01',
                         'revision': '01',
                         'slot': '04:00.0',
                         'vendor_id': '144d',
                         'vendor_name': 'Samsung Electronics Co Ltd'},
                        {'class_id': '0604',
                         'class_name': 'PCI bridge',
                         'device_id': '156d',
                         'device_name': 'Device',
                         'driver': 'pcieport',
                         'slot': '05:00.0',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0604',
                         'class_name': 'PCI bridge',
                         'device_id': '156d',
                         'device_name': 'Device',
                         'driver': 'pcieport',
                         'slot': '06:00.0',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0604',
                         'class_name': 'PCI bridge',
                         'device_id': '156d',
                         'device_name': 'Device',
                         'driver': 'pcieport',
                         'slot': '06:03.0',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0604',
                         'class_name': 'PCI bridge',
                         'device_id': '156d',
                         'device_name': 'Device',
                         'driver': 'pcieport',
                         'slot': '06:04.0',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0604',
                         'class_name': 'PCI bridge',
                         'device_id': '156d',
                         'device_name': 'Device',
                         'driver': 'pcieport',
                         'slot': '06:05.0',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0604',
                         'class_name': 'PCI bridge',
                         'device_id': '156d',
                         'device_name': 'Device',
                         'driver': 'pcieport',
                         'slot': '06:06.0',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0880',
                         'class_name': 'System peripheral',
                         'device_id': '156c',
                         'device_name': 'Device',
                         'driver': 'thunderbolt',
                         'sdevice_id': '1111',
                         'sdevice_name': 'Device',
                         'slot': '07:00.0',
                         'svendor_id': '2222',
                         'svendor_name': 'Unknown vendor',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0604',
                         'class_name': 'PCI bridge',
                         'device_id': '1549',
                         'device_name': 'DSL3510 Thunderbolt Controller [Cactus Ridge]',
                         'driver': 'pcieport',
                         'slot': '08:00.0',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0604',
                         'class_name': 'PCI bridge',
                         'device_id': '1549',
                         'device_name': 'DSL3510 Thunderbolt Controller [Cactus Ridge]',
                         'driver': 'pcieport',
                         'slot': '09:00.0',
                         'vendor_id': '8086',
                         'vendor_name': 'Intel Corporation'},
                        {'class_id': '0200',
                         'class_name': 'Ethernet controller',
                         'device_id': '1682',
                         'device_name': 'NetXtreme BCM57762 Gigabit Ethernet PCIe',
                         'driver': 'tg3',
                         'sdevice_id': '00f6',
                         'sdevice_name': 'Device',
                         'slot': '0a:00.0',
                         'svendor_id': '106b',
                         'svendor_name': 'Apple Inc.',
                         'vendor_id': '14e4',
                         'vendor_name': 'Broadcom Corporation'}]}}
13923
11061
1327.80075073

Process finished with exit code 0
```