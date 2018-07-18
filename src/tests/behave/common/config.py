import collections
import copy
import os

from conflagration import api
from conflagration.namespace import ModifiableNamespace
from src.tests.behave.common.const import ConfigVars, Sources


DEFAULT_CONFIG_FILES = (
    #'src/tests/behave/configs/mercury_tests_creds.config',
    #'src/tests/behave/configs/mercury_tests.config',
    # USE ENVIRONMENT VARIABLES
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
