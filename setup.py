# Copyright 2017 Rackspace Hosting
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
import importlib
import json
import os
import re
import sys
from setuptools import setup, find_packages


pkg_groups = {
    'agent': ['mercury-agent', 'mercury-common'],
    'client': ['mercury-client'],
    'server': [
        'mercury-rpc', 'mercury-inventory', 'mercury-log', 'mercury-proxy',
        'mercury-common']}
pkg_groups['all'] = set([y for x in pkg_groups.keys() for y in pkg_groups[x]])
    

packages = []
pkg_list = find_packages(exclude=('tests', 'tests.*', '*.tests.*', '*.tests'))
for pkg in pkg_list:
    source = pkg
    tmp = pkg.split('.')[1:]
    if not tmp:
        continue
    name = tmp[0]
    pkg_name = '.'.join(tmp[1:])
    pkg_data = './src/' + '/'.join(tmp) + '/*'
    setup_file = os.path.join(os.getcwd(), 'src', name, 'setup.py')
    if not os.path.isfile(setup_file) or name in [p['name'] for p in packages]:
        setup_file = None
    packages.append({
        'name': name,
        'pkg_name': pkg_name,
        'pkg_data': pkg_data,
        'setup_file': setup_file,
    })


# This data will be dynamically updated based on the pkg info above and setup.py contents.
config = dict(
    name='mercury',
    version='0.0.1',
    packages=[],
    include_package_data=True,
    package_data={},
    package_dir={},
    namespace_packages=[],
    url='https://www.rackspace.com',
    license='Apache 2.0',
    author='',
    author_email='',
    description='',
    install_requires=[]
)

ignore_keywords = [
    'build', 'egg-info', 'dist', 'scratch', 'doc', 'tests', '__pycache__']


def ignore_check(folder):
    for i in ignore_keywords:
        if folder.endswith(i) or i in folder.split('/'):
            return True
    return False


def check_init(
    filename, txt="__import__('pkg_resources').declare_namespace(__name__)"
):
    with open(filename, 'r') as f:
        return any(txt in line for line in f)


def update_init(
    filename, txt="__import__('pkg_resources').declare_namespace(__name__)"
):
    with open(filename, 'a+') as f:
        f.write('\n{}\n'.format(txt))


def namespace_init(folder='.'):
    for foldername, subfolders, filenames in os.walk(folder):
        if not ignore_check(foldername):
            for subfolder in [x for x in subfolders]:
                namespace_init(subfolder)
            if '__init__.py' in filenames:
                if not check_init(os.path.join(foldername, '__init__.py')):
                    update_init(os.path.join(foldername, '__init__.py'))
            else:
                update_init(os.path.join(foldername, '__init__.py'))


def merge_config(pkg):
    """This merges setup configs with the local config."""
    if pkg['setup_file']:
        setup_mod = importlib.import_module(
            re.sub(r'.*{}'.format('src'), 'src',
                pkg['setup_file']).replace('/', '.')[:-3])
        if not config['author']:
            config['author'] = setup_mod.config['author']
        if not config['author_email']:
            config['author_email'] = setup_mod.config['author_email']
        config['description'] = '{}[{}]\n{}\n'.format(
            config['description'], pkg['name'],
            setup_mod.config['description'])
        config['install_requires'] = (
            config['install_requires'] + list(
                set(setup_mod.config['install_requires']) -
                set(config['install_requires'])
            ))
        if 'entry_points' in setup_mod.config.keys():
            config['entry_points'] = setup_mod.config['entry_points']
    if not pkg['pkg_name']:
        return
    if pkg['pkg_name'] not in config['packages']:
        config['packages'].append(pkg['pkg_name'])
        config['package_data'][pkg['pkg_name']] = [pkg['pkg_data']]
        config['namespace_packages'].append(pkg['pkg_name'])
        config['package_dir'][pkg['pkg_name']] = pkg['pkg_data'][:-2]

    config['package_data']['mercury'] = ['/src/*']

# Default behavior if no target passed.
if not [a for a in sys.argv if a.startswith('--')]:
    sys.argv.append('--all')


### Check for install target in sys.argv Ex 'python setup.py install --agent'
for g in pkg_groups.keys():
    if '--' + g in sys.argv:
        for p in pkg_groups[g]:
            for pkg in packages:
                if p in pkg['name']:
                    merge_config(pkg)
        sys.argv.remove('--' + g)
    else:
        for n in [x['name'] for x in packages]:
            if '--' + n in sys.argv:
                for pkg in packages:
                    if n in pkg['name']:
                        merge_config(pkg)
                sys.argv.remove('--' + n)


# print(json.dumps(config, sort_keys=True, indent=4, separators=(',', ': ')))
namespace_init('./src')
setup(**config)
