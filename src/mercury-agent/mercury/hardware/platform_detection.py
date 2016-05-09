def get_vendor(dmi_info):
    return dmi_info.get('sys_vendor')


def is_platform(dmi_info, platform):
    return get_vendor(dmi_info) == platform


def is_dell(dmi_info):
    return is_platform(dmi_info, 'Dell Inc.')


def is_hp(dmi_info):
    return is_platform(dmi_info, 'HP')


def is_quanta(dmi_info):
    return is_platform(dmi_info, 'Quanta')


def get_product_name(dmi_info):
    return dmi_info.get('product_name')


# PCI
def has_smart_array_gen9(pci_data):
    device_id = "3239"  # Smart Array Gen9 Controllers
    for device in pci_data:
        if device['device_id'] == device_id:
            return True
    return False
