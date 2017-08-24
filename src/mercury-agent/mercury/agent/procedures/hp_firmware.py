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

import glob
import logging
import os

import lxml
import requests

from mercury.agent.capabilities import capability
from mercury.common.exceptions import HPFirmwareException
from mercury.common.helpers import cli
from mercury.hardware.platform_detection import is_hp

log = logging.getLogger(__name__)
firmware_path = '/tmp/hp/firmware'


def _extract(tarball_path, extract_path):
    os.makedirs(extract_path)
    log.info('Extracting {0}'.format(tarball_path))
    cmd = 'tar --strip-components=1 -xvf {0} -C {1}'.format(tarball_path,
                                                            extract_path)

    result = cli.run(cmd)
    if result.returncode:
        log.error('Could not extract archive: {0}'.format(result))
        return False

    return True


def parse_fw_report(xml_file):
    # noinspection PyUnresolvedReferences
    fw_tree = lxml.etree.parse(xml_file)
    # For checking needs_install XML tag is present or not
    component_list = parse_xml_for_components(fw_tree, 'needs_install')
    component_list += parse_xml_for_components(fw_tree, 'already_installed')
    return component_list


def parse_xml_for_components(xml_tree, xml_tag):
    def strip_date(version):
        return version.split('-')[0]

    component_list = []
    for i in xml_tree.findall(".//{0}/component".format(xml_tag)):
        installed = strip_date(i.find("installedversion").text)
        available = strip_date(i.find("version").text)
        component_name = i.find("name").text
        component_list.append(dict(name=component_name,
                                   installed=installed,
                                   available=available))
    return component_list


def find_available_updates():
    component_list = parse_fw_report(generate_fw_report())
    return firmware_updates_available(component_list)


def firmware_updates_available(component_list):
    update_flag = False
    for comp in component_list:
        log.debug('COMPONENT: {0}'.format(comp['name']))
        if comp['installed'].replace(' ', '') not in \
                comp['available'].replace(' ', ''):
            log.debug('CURRENT: {0}'.format(comp['installed']))
            log.debug('TARGET: {0}'.format(comp['available']))
            update_flag = True
        else:
            log.info('Firmware is up to date: {0}'.format(comp['available']))
    return update_flag


def _hpsum_cmd(cmd):
    # TODO: Figure out how to have cli.run() support timeouts
    # Agent probably already supports timeout for capabilities, verify!
    hpsum_exec_path = os.path.join(firmware_path, 'hpsum')
    command = '{0} /s {1}'.format(hpsum_exec_path, cmd)
    return cli.run(command)


def generate_fw_report():
    result = _hpsum_cmd('/report')
    if result.returncode:
        raise HPFirmwareException('Unable to generate firmware report')

    xml_report = glob.glob(os.path.join(firmware_path, 'HPSum*'))
    if not xml_report:
        raise HPFirmwareException('Unable to find generated firmware report')

    return xml_report[0]


def get_return_code_status(ret):
    # Return codes for HP firmware updates.. supposedly for Linux
    ret_code = dict(
        HP_SUCCESS_NO_REBOOT=0,
        HP_SUCCESS_REBOOT=1,
        HP_SUCCESS_NOT_REQUIRED=3,
        HP_FAILURE_GENERAL=-1,
        HP_FAILURE_BAD_PARM=-2,
        HP_FAILURE_COMPONENT_FAILED=-3,
        HP_COMMAND_FAILURE=-4
    )

    for k in ret_code:
        if ret_code[k] == ret:
            ret = k

    return_code_status = dict(
        HP_SUCCESS_NO_REBOOT=dict(
            error_state=False,
            message='Firmware installation was successful and no reboot required',
            reboot_flag=False),
        HP_SUCCESS_REBOOT=dict(
            error_state=False,
            message='Firmware installation was successful and reboot is required',
            reboot_flag=True),
        HP_SUCCESS_NOT_REQUIRED=dict(
            error_state=False,
            message='Firmware installation successful and no update required',
            reboot_flag=False),
        HP_FAILURE_GENERAL=dict(
            error_state=True,
            message='General failure, check hpsum_log for errors',
            reboot_flag=False),
        HP_FAILURE_BAD_PARM=dict(
            error_state=True,
            message='Bad input parameter, check hpsum_log for errors',
            reboot_flag=False),
        HP_FAILURE_COMPONENT_FAILED=dict(
            error_state=True,
            message='Installation of component failed, check hpsum_logs for errors',
            reboot_flag=False),
        HP_COMMAND_FAILURE=dict(
            error_state=True,
            message='The CLI command execution failed',
            reboot_flag=False)
    )
    return return_code_status[ret]


def install_updates(force_install):
    log.info('Flashing firmware for this box')
    # Using /On_failed_dependency:Force parameter to avoid failed dependencies
    if force_install:
        log.info('Forcefully upgrading firmware. This may take sometime..')
        return _hpsum_cmd('/f /On_failed_dependency:Force')

    return _hpsum_cmd('/On_failed_dependency:Force')


def parse_log_output_for_errors():
    """
    Sample huspm log output for fetching exit code:
    ////////////////////////////////////////////////////////////////////////////////
    //  Exit Code for Node localhost: 1
    //  HP Smart Update Manager for Node localhost Finished Fri Jan 15 2016 15:39:09
    ////////////////////////////////////////////////////////////////////////////////
    """
    hpsum_log_path = '/var/hp/log/localhost/hpsum_log.txt'
    exit_code = None
    with open(hpsum_log_path) as f:
        contents = f.readlines()

    for line in contents:
        if 'Exit Code' in line:
            exit_code = line.split(':')[1]

    status = get_return_code_status(int(exit_code))
    log.info(status.get('message'))
    if status.get('error_state'):
        raise HPFirmwareException('Flashing failed with exit code {0}'.format(
            exit_code))
    return status.get('reboot_flag')


@capability('hp_apply_bios_settings',
            description='Apply bios settings found in given file',
            kwarg_names=['url'], serial=True,
            dependency_callback=is_hp, timeout=60)
def hp_apply_bios_settings(url=None):
    """
    Apply BIOS settings found at the given URL

    :param url: Full URL to the BIOS file
    """
    # TODO: Implement this
    # TODO: Alongside the conrepfile, some blobs have to be installed to bring
    # certain components up to a recommended version. Who determines which blobs
    # to execute? Are they provided or does this method
    # keep track of those based on the model
    ########
    # Consider writing a generic conrep interface, rather than relying on these
    # legacy interfaces. If the firmware needs to be updated prior to certain settings
    # being available, use the hp_update_firmware method first, rather than orchestrating
    # the upgrades here.
    # - Jared
    #########
    # DL380Gen9 = HPServer(name="ProLiant DL380 Gen9",
    #                      cfg='DL380Gen9_conrep_RAX.dat',
    #                      blobs=['BCM5719_2.13.5_RHEL6.scexe',
    #                             'HPSA_1.18_RHEL6.scexe',
    #                             'iLO4_2.02_RHEL6.scexe'])

    assert url
    raise NotImplementedError


@capability('hp_update_firmware',
            description='Installs updates from provided packages',
            kwarg_names=['url', 'dry_run'], serial=True,
            dependency_callback=is_hp, timeout=3600)
def hp_update_firmware(url=None, dry_run=False):
    """
    Apply HP firmware updates

    :param url: Full URL to the package containing firmware files
    :param dry_run: If firmware updates should be applied when found
    """
    try:
        r = requests.get(url, stream=True, verify=False)
    except requests.RequestException as err:
        log.error('There was an error in retrieving the '
                  'firmware package: {}'.format(err))
        return

    download_path = '/tmp/hpfirmware.tar.gz'
    with open(download_path, 'wb') as f:
        for chunk in r.iter_content(1024 ** 2):
            if chunk:
                f.write(chunk)

    if not _extract(download_path, firmware_path):
        return

    updates_available = find_available_updates()
    if dry_run:
        if updates_available:
            log.info('Updates were available but were not installed')
        return

    # Return code could be a false positive, check log file output
    install_updates(updates_available)
    reboot_required = parse_log_output_for_errors()
    return dict(result=dict(return_code=1, success=True, reboot_required=reboot_required))
