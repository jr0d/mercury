import argparse
import functools
import os
import os.path
import sys

import yaml


class ConfigWrapper(object):

    def __init__(self, system):
        print("Handling: {0}".format(system))
        self.system = system

    @staticmethod
    def get_config_dir(base_path=None):
        return "{0}/.mercury".format(
            os.environ['HOME']
            if 'HOME' in os.environ
            else (
                '/root'
                if base_path is None
                else base_path
            )
        )

    def read_sample_config(self):
        print("Generating Config file for {0}".format(self.system))
        sample_config_file = (
            "./src/mercury-{0}/mercury-{0}-sample.yaml".format(
                self.system
            )
        )
        print("Reading Config File: {0}".format(sample_config_file))
        with open(sample_config_file, 'r') as sample_config_input:
            data = sample_config_input.read()
            print("\tRead Data:\n{0}".format(data))
            return yaml.load(data)

    def write_target_config(self, base_path, data):
        # ensure the directory exists
        output_dir = ConfigWrapper.get_config_dir(base_path)
        print("Output Directory: {0}".format(output_dir))
        print("\tValidating directory exists")
        if not os.path.exists(output_dir):
            print("\tCreating directory ${0}".format(output_dir))
            os.makedirs(output_dir, mode=0o700, exist_ok=True)

        output_config = '/'.join(
            [
                output_dir,
                'mercury-{0}.yaml'.format(self.system)
            ]
        )
        print("Output Config File: {0}".format(output_config))
        with open(output_config, 'w') as sample_config_output:
            # note: `yaml.dump` uses two means of output - flow style
            #   and block style. If it has "nested collections" it
            #   uses the block style; otherwise it uses the flow style.
            #   By setting `default_flow_style` to `False` we force
            #   it to always use the block style and thus give the
            #   same output style as the input data
            encoded_data = yaml.dump(
                data,
                default_flow_style=False
            )
            print("\tWriting Data:\n{0}".format(encoded_data))
            sample_config_output.write(encoded_data)


    #@functools.wraps
    def __call__(self, fn, *args, **kwargs):
        print("Wrapped Function for {0}".format(self.system))
        print("Positional Arguments: {0}".format(args))
        print("Keyword Arguments: {0}".format(kwargs))

        def wrapped(*args, **kwargs):
            print("Called for {0}".format(self.system))
            print("Positional Arguments: {0}".format(args))
            print("Keyword Arguments: {0}".format(kwargs))

            options = args[0]
            # load the config data into the kwargs
            new_kwargs = {
                'config_data': self.read_sample_config()
            }
            new_kwargs.update(kwargs)
            print("Updated Keyword Arguments: {0}".format(new_kwargs))

            # update the config data
            try:
                print("Processing...")
                updated_config = fn(*args, **new_kwargs)
            except LookupError as ex:
                print('Error updating config: {0}'.format(ex))
                return

            print("Config update complete.\nSaving...")
            # update the config data and write it
            self.write_target_config(options.base_path, updated_config)
            print("Config Saved")

        return wrapped


@ConfigWrapper('inventory')
def update_inventory_config(options, config_data=None):
    config_data['inventory']['db']['servers'] = [
        options.database
    ]
    config_data['inventory']['db']['replica_name'] = options.replica_name
    config_data['inventory']['bind_address'] = options.inventory_router

    return config_data


@ConfigWrapper('log')
def update_log_config(options, config_data=None):
    config_data['log_service']['db']['servers'] = [
        options.database
    ]
    config_data['log_service']['db']['replica_name'] = options.replica_name
    config_data['log_service']['bind_address'] = options.log_url

    return config_data

@ConfigWrapper('rpc')
def update_rpc_config(options, config_data=None):
    config_data['rpc']['inventory_router'] = options.inventory_router

    config_data['rpc']['db']['servers'] = [
        options.database
    ]
    config_data['rpc']['db']['replica_name'] = options.replica_name

    config_data['rpc']['redis']['host'] = options.redis_host
    config_data['rpc']['redis']['port'] = options.redis_port

    config_data['rpc']['frontend']['bind_address'] = 'tcp://{0}:{1}'.format(
        options.frontend_host,
        options.frontend_port
    )
    config_data['rpc']['backend']['bind_address'] = 'tcp://{0}:{1}'.format(
        options.backend_host,
        options.backend_port
    )

    config_data['rpc']['origin']['public_address'] = options.info_address
    config_data['rpc']['origin']['frontend_port'] = options.frontend_port

    return config_data


def main():
    arg_parser = argparse.ArgumentParser(
        description="Mercury Automated Configurator for Docker"
    )

    arg_parser.add_argument(
        '--base-path',
        required=False,
        type=str,
        default=(
            os.environ['HOME']
            if 'HOME' in os.environ
            else (
                '/root'
                if base_path is None
                else base_path
            )
        )
    )

    def add_mongo(subparser):
        subparser.add_argument(
            '--database', '-db',
            required=False,
            type=str,
            default="localhost:27017"
        )
        subparser.add_argument(
            '--replica-name', '-rn',
            required=False,
            type=str,
            default=None
        )
    def add_inventory_router(subparser):
        subparser.add_argument(
            '--inventory-router',
            required=False,
            type=str,
            default="tcp://localhost:9000"
        )

    command_parser = arg_parser.add_subparsers(
        title='command'
    )
    inventory_config_parser = command_parser.add_parser(
        "inventory"
    )
    add_mongo(inventory_config_parser)
    add_inventory_router(inventory_config_parser)
    inventory_config_parser.set_defaults(operative=update_inventory_config)

    log_config_parser = command_parser.add_parser(
        "log"
    )
    add_mongo(log_config_parser)
    log_config_parser.add_argument(
        '--log-url',
        required=False,
        type=str,
        default="tcp://0.0.0.0:9006"
    )
    log_config_parser.set_defaults(operative=update_log_config)

    rpc_config_parser = command_parser.add_parser(
        "rpc"
    )
    add_mongo(rpc_config_parser)
    add_inventory_router(rpc_config_parser)
    rpc_config_parser.add_argument(
        '--redis-host', '-rh',
        required=False,
        type=str,
        default="localhost"
    )
    rpc_config_parser.add_argument(
        '--redis-port', '-rp',
        required=False,
        type=int,
        default=6379
    )
    rpc_config_parser.add_argument(
        '--frontend-host',
        required=False,
        type=str,
        default="0.0.0.0"
    )
    rpc_config_parser.add_argument(
        '--backend-host',
        required=False,
        type=str,
        default="0.0.0.0"
    )
    rpc_config_parser.add_argument(
        '--frontend-port',
        required=False,
        type=int,
        default=9001
    )
    rpc_config_parser.add_argument(
        '--backend-port',
        required=False,
        type=str,
        default=9002
    )
    rpc_config_parser.add_argument(
        '--info-address',
        required=False,
        type=str,
        default="localhost"
    )
    rpc_config_parser.set_defaults(operative=update_rpc_config)

    options = arg_parser.parse_args()
    options.operative(options)
    return 0


if __name__ == "__main__":
    sys.exit(main())
