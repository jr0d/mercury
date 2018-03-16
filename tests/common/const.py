class ConfigVars(object):
    """Configuration environment variables"""

    # behavior
    VERBOSE = 'VERBOSE'

    # Mercury API URL
    MIGRATOR_API_ENDPOINT = 'MIGRATOR_API_ENDPOINT'
    # TODO some of these probably just belong in this file in another Class
    # instead of being defined in a config file (like 'mercury_id')
    ENTITY_FIELD_NAME = 'ENTITY_FIELD_NAME'
    LISTED_SERVICE_NAMES = 'LISTED_SERVICE_NAMES'
    INTERNAL_IDENTITY_URL = 'INTERNAL_IDENTITY_URL'
    INTERNAL_IDENTITY_USERNAME = 'INTERNAL_IDENTITY_USERNAME'
    INTERNAL_IDENTITY_PASSWORD = 'INTERNAL_IDENTITY_PASSWORD'
    DOMAIN = 'DOMAIN'
    DOMAIN_NAME = 'DOMAIN_NAME'

class Sources(object):
    """Sources to get the configuration variables from"""

    ENVIRON = 'environ'
