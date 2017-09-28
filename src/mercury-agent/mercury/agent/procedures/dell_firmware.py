# Copyright 2015 Jared Rodriguez (jared.rodriguez@rackspace.com, hussamd@gmail.com,
# prashantvm89@gmail.com, lee.scott@rackspace.com, Chris.Griffith@rackspace.com)
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

import logging
import os

from mercury.agent.capabilities import capability
from mercury.hardware.platform_detection import is_dell
from mercury.common.exceptions import MercuryFirmwareException
from mercury.common.helpers.util import extract_tar_archive, download_file, cli, xml_to_dict


log = logging.getLogger(__name__)
firmware_path = '/tmp/dell/firmware'


def get_return_code_status(ret):
        # Return codes for DELL firmware updates.. supposedly for Linux
        ret_code = dict(
            SUCCESS_NO_REBOOT=0,
            FAILURE=1,
            SUCCESS_REBOOT_REQUIRED=2,
            DEP_SOFT_ERROR=3,
            DEP_HARD_ERROR=4,
            QUAL_HARD_ERROR=5,
            REBOOTING_SYSTEM=6,
            RPM_VERIFY_FAILED=9,
            UPDATE_SUCCESSFUL_SOFT_DEPEDENCY_NOT_MET=13,
            REBOOT_REQUIRED_SOFT_DEPENDENCY_NOT_MET=14
        )

        for k in ret_code:
            if ret_code[k] == ret:
                ret = k

        return_code_status = dict(
            SUCCESS_NO_REBOOT=dict(
                error_state=False,
                message='Update was successful and no reboot required',
                reboot_flag=False),
            FAILURE=dict(
                error_state=True,
                message='Update was unsuccessful (Failure)',
                reboot_flag=False),
            SUCCESS_REBOOT_REQUIRED=dict(
                error_state=False,
                message='Update was successful and reboot is required',
                reboot_flag=True),
            DEP_SOFT_ERROR=dict(
                error_state=True,
                message='Soft dependency error',
                reboot_flag=False),
            DEP_HARD_ERROR=dict(
                error_state=True,
                message='Hard dependency errors',
                reboot_flag=False),
            QUAL_HARD_ERROR=dict(
                error_state=True,
                message='Qualification error',
                reboot_flag=False),
            REBOOTING_SYSTEM=dict(
                error_state=False,
                message='Rebooting system',
                reboot_flag=True),
            RPM_VERIFY_FAILED=dict(
                error_state=True,
                message='RPM verification has failed',
                reboot_flag=False),
            UPDATE_SUCCESSFUL_SOFT_DEPEDENCY_NOT_MET=dict(
                error_state=False,
                message='Update is successful. Soft Dependencies are not met.',
                reboot_flag=False),
            REBOOT_REQUIRED_SOFT_DEPENDENCY_NOT_MET=dict(
                error_state=False,
                message='Update is successful. Reboot is required. Soft Dependencies are not met.',
                reboot_flag=True)
        )
        return return_code_status[ret]


def run_cmd_and_parse_xml(cmd, xml_element):
    result = cli.run(cmd)
    return xml_to_dict(result.stdout, xml_element)


def _split_and_get_fw_vers(xml_element_dict, xml_ele):
    fw_vers = []
    for xml_element in xml_element_dict:
        split_value = str(xml_element[xml_ele]).split()
        if not split_value:
            continue
        # DRAC special case
        if 'FWVersion' in xml_ele:
            fw_vers.append(split_value[0])
        else:
            fw_vers.append(split_value[1 if len(split_value) > 1 else 0])
    return set(fw_vers)


def _get_runner(args, xml_element, xml_tag):
    command = 'omreport {} -fmt xml'.format(args)
    xml_element_dict = run_cmd_and_parse_xml(command, xml_element)
    return _split_and_get_fw_vers(xml_element_dict, xml_tag)


def get_nics_fw():
    return _get_runner('chassis nics', './/DevNicObj', 'FirmwareVersion')


def get_storage_controller_fw():
    return _get_runner('storage controller', './/DCStorageObject', 'FirmwareVer')


def get_bios_fw():
    return _get_runner('chassis bios', './/SystemBIOS', 'Version')


def get_drac_fw():
    return _get_runner('chassis firmware', './/Firmware', 'FWVersion')


def generate_fw_report():
    return {
        'BIOS': get_bios_fw(),
        'DRAC': get_drac_fw(),
        'Storage Controller': get_storage_controller_fw(),
        'Network Adapter': get_nics_fw()
    }


def parse_fw_report(existing_firmware):
    component_list = []
    for component_name, installed_versions in existing_firmware.iteritems():
        for ver in installed_versions:
            component_list.append({
                'name': component_name,
                'version': ver,
                'is_installed': any(
                    (ver in installer)
                    for installer in os.listdir(firmware_path)
                )
            })
    return component_list


def firmware_updates_available(component_list):
    update_flag = False
    for comp in component_list:
        log.info(('COMPONENT: {0}'.format(comp['name'])))
        if comp['is_installed']:
            log.info('Firmware is up to date {0}'.format(comp['version']))
        else:
            log.info('CURRENT: {0}'.format(comp['version']))
            log.info('TARGET: Higher version is available')
            update_flag = True
    return update_flag


def find_available_updates():
    # omreport command works without sudo
    component_list = parse_fw_report(generate_fw_report())
    return firmware_updates_available(component_list)


def _check_all():
        update_list = list()
        check_args = ['-q', '-c']

        for installer in os.listdir(firmware_path):
            check_cmd = os.path.join(firmware_path, installer)
            check_cmd = [check_cmd] + check_args
            result = cli.run(check_cmd)
            if result.returncode == 5:
                log.info('{0} is not applicable'.format(installer))
            elif result.returncode == 3:
                log.info('{0} is already updated'.format(installer))
            else:
                log.info('{0} update must run'.format(installer))
                update_list.append(installer)
        return update_list


def install_updates():
    reboot_required = False
    log.debug('Flashing firmware for this box')
    update_list = _check_all()
    if not update_list:
        log.debug('All firmware is up to date')
        return reboot_required

    errors = []
    for installer in update_list:
        update_cmd = os.path.join(firmware_path, installer)
        update_cmd = [update_cmd] + ['-q']
        log.info('Running update: {0}'.format(installer))
        result = cli.run(update_cmd)
        status = get_return_code_status(int(result.returncode))
        if status.get('error_state'):
            err_msg = '{0}: {1}'.format((status.get('message')), result)
            log.error(err_msg)
            errors.append(err_msg)
        else:
            reboot_required = True
    if errors:
        raise MercuryFirmwareException("Errors while flashing Dell Firmware: "
                                       "{}".format(", ".join(errors)))
    return reboot_required


@capability('dell_apply_bios_settings',
            description='Apply bios settings found in given file',
            kwarg_names=['url'], serial=True,
            dependency_callback=is_dell, timeout=600)
def dell_apply_bios_settings(url=None):
    """
    Apply BIOS settings found at the given URL

    :param url: Full URL to the BIOS file
    """
    # TODO: Implement this
    assert url
    raise NotImplementedError


@capability('dell_update_firmware',
            description='Installs updates from provided packages',
            kwarg_names=['url', 'dry_run'], serial=True,
            dependency_callback=is_dell, timeout=3600)
def dell_update_firmware(url, dry_run=False):
    """
     Apply HP firmware updates
     :param url: Full URL to the package containing firmware files
     :param dry_run: If firmware updates should be applied when found
    """
    download_path = '/tmp/dell_firmware.tar.gz'

    download_file(url, download_path)

    result = extract_tar_archive(download_path, firmware_path)
    if result.returncode:
        raise MercuryFirmwareException('Could not extract firmware file: {}'.format(result))

    updates_available = find_available_updates()
    if dry_run:
        if updates_available:
            log.info('Updates were available but were not installed')
        return

    # Return code could be a false positive, check log file output
    reboot_required = install_updates()
    # TODO: Implement a reboot capability?
    return dict(result=dict(return_code=1, success=True, reboot_required=reboot_required))
