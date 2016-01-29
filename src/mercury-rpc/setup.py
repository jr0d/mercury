from setuptools import setup

setup(
    name='mercury-rpc',
    version='0.0.1',
    packages=['mercury'],
    url='https://www.rackspace.com',
    license='',
    author='Jared Rodriguez',
    author_email='jared.rodriguez@rackspace.com',
    description='',
    install_requires=[
        'pyzmq',
        'msgpack-python',
        'pymongo',
    ]
)
