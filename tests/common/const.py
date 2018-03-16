class ConfigVars(object):
    """Configuration environment variables"""

    # behavior
    VERBOSE = 'VERBOSE'

    # Mercury API URL
    MIGRATOR_API_ENDPOINT = 'MIGRATOR_API_ENDPOINT'

class Sources(object):
    """Sources to get the configuration variables from"""

    ENVIRON = 'environ'
