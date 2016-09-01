import sys
import argparse

URL = 'http://mercury:9005'

parser = argparse.ArgumentParser(description='MERCURY ProtoCLI pre-alpha')
parser.add_argument('-m', '--mercury_url')
subparsers = parser.add_subparsers(dest='command')

rpc_parser = subparsers.add_parser('rpc')
rpc_parser.add_argument('query')
rpc_parser.add_argument('command')
rpc_parser.add_argument('-a', '--args')
rpc_parser.add_argument('-k', '--kwargs')

press_parser = subparsers.add_parser('press')
press_parser.add_argument('query')
press_parser.add_argument('-a', '--asset-path')
press_parser.add_argument('-p', '--press-template')


def main():
    namespace = parser.parse_known_args(sys.argv[1:])
    print(namespace)


if __name__ == '__main__':
    main()
