import json
import yaml
from mercury.client.rpc import ActiveComputers

from rax_io import config, execution, assets

ac = ActiveComputers(config.MERCURY)


def configuration_from_yaml(path):
    with open(path) as fp:
        return yaml.load(fp)


def press_system(targets, path):
    configuration = configuration_from_yaml(path)

    execution.execute(targets, 'press', kwargs={
        'configuration': configuration
    })


def press_system_preprocessor(targets, path):
    with open(path) as fp:
        template = fp.read().splitlines()

    instruction = {
        'preprocessor': 'press_static_assets',
        'template': template,
        'assets': assets.generate_assets_for_targets(targets)
    }

    # print(instruction)
    execution.preprocessor_exec(targets, instruction)


if __name__ == '__main__':
    # target = {
    #     'mercury_id': '010f832128902b30e333a4ac241533ca1c4b1d05ae'
    # }
    #
    # press_system(target, './press/centos_k8.yaml')

    import argparse
    parser = argparse.ArgumentParser(description="Execute mercury commands")
    parser.add_argument('query', help="The target query")
    parser.add_argument('configuration_path', help='Path press configuration')

    namespace = parser.parse_args()

    press_system_preprocessor(json.loads(namespace.query),
                              namespace.configuration_path)

