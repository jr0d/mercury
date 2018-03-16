import collections
import copy
import os

from conflagration import api
from conflagration.namespace import ModifiableNamespace
from tests.common.const import ConfigVars, Sources


DEFAULT_CONFIG_FILES = (
    'tests/configs/mercury_tests_creds.config',
    'tests/configs/mercury_tests.config',
)


def get_conflagration(config_file_paths=DEFAULT_CONFIG_FILES):
    """Instantiate a conflagration instance.

    This defaults to loading from two files:

    1. mercury_tests_creds.config - contains sensitive information
    2. mercury_tests.config - contains non-sensitive information

    This lets us encrypt just the sensitive bits for jenkins and quickly make
    changes to the non-sensitive configs, which we can store in plaintext.
    """
    here = os.getcwd()
    paths = [os.path.join(here, filename) for filename in config_file_paths]
    if config_file_paths:
        cfg = api.conflagration(files=paths, namespace_obj=ModifiableNamespace())
    else:
        cfg = api.conflagration(default_to_env=True)
    return cfg


class Config(object):
    """
    Class to manage and get configuration variable values from Keyring
    and/or environment variables.For ex.

    >>> from tests.common.config import Config
    >>> config = Config(set_all=True)
    >>> config.mercury_api_endpoint
    """
    # TODO 'http://0.0.0.0:5000'

    def __init__(self, mercury_api_endpoint=None, verbose=None):

        # Class attributes used for storing configuration values

        self.mercury_api_endpoint = mercury_api_endpoint
        self.verbose = verbose

        # These should match all the variables from ConfigVars and would be
        # expected as environment variables in upper case, or keyring system
        # variables in lower case.
        self.config_vars = [val for attr, val in vars(ConfigVars).items()
                            if not attr.startswith('_')]


        # Sources to get the config variable values.
        self.sources = [Sources.ENVIRON]

        # Set all self.config_vars from all self.sources
        if set_all:
            self.set_from_sources()

    def set_from_sources(self, config_vars=None, sources=None):
        """
        Setting class attributes from the sources. For ex. if RAX_PASSWORD,
        is set as rax_password in the system keyring storage, this method will
        set the rax_password class attribute value; or if the RAX_API_KEY
        is set as an environment variable, this method will set the
        rax_api_key class attribute value.

        :param list(str) config_vars: subset of self.config_vars (upper case)
            Their corresponding class attribute will be set if there is a
            value from a given source like keyring or environ.
        :param list(str) sources: subset of self.sources. List of sources where
            to get the config values from. Order will be followed, for ex. if
            RAX_PASSWORD exists in keyring and environ, the last one will
            overwrite the value from the first one.
        """

        if not config_vars:
            config_vars = self.config_vars
        if not sources:
            sources = self.sources

        for var in config_vars:
            var_name = getattr(ConfigVars, var)
            value = None

            # System variables are expected to be in lower case
            # Get the values from environment variables first to try to avoid
            # errors with keyring and the venv.
            # TODO Find a better solution for getting the credentials,
            # TODO possibly a config file or password safe solution
            if Sources.ENVIRON in sources:
                environ_value = os.environ.get(var_name)
                if environ_value:
                    value = environ_value

            setattr(self, var_name.lower(), value)

    def reset(self, config_vars=None):
        """
        Setting to None the class attributes used for config variables.

        :param list(str) environ_vars: subset of self.environ_vars (upper case)
            Their corresponding class attribute will be set to None.
        """

        if not config_vars:
            config_vars = self.config_vars

        for var in config_vars:
            var_name = getattr(ConfigVars, var).lower()
            setattr(self, var_name, None)

    def __repr__(self):
        """
        Representing custom config data
        """
        data = copy.deepcopy(self.__dict__)
        config_vars = data.pop('config_vars')
        sources = data.pop('sources')

        vars_to_show = collections.OrderedDict(sorted(data.items()))

        msg = ['Configuration Variables']
        for key, value in vars_to_show.items():
            s = '{0}: {1}'.format(key, value)
            msg.append(s)

        s = '\nSources: {0}'.format(sources)
        msg.append(s)
        s = '\nVariable names to be used: {0}'.format(config_vars)
        msg.append(s)
        s = ('\nNote: Enviroment variables names should be in upper case and '
             'Keyring variables names should be in lower case.')
        msg.append(s)

        res = '\n'.join(msg)
        return res
