class ConfigVars(object):
    """Configuration environment variables"""

    # behavior
    VERBOSE = 'VERBOSE'

    # Mercury API URL
    MERCURY_API_ENDPOINT = 'MERCURY_API_ENDPOINT'
    # Identity
    INTERNAL_IDENTITY_URL = 'INTERNAL_IDENTITY_URL'
    INTERNAL_IDENTITY_USERNAME = 'INTERNAL_IDENTITY_USERNAME'
    INTERNAL_IDENTITY_PASSWORD = 'INTERNAL_IDENTITY_PASSWORD'
    DOMAIN = 'DOMAIN'
    DOMAIN_NAME = 'DOMAIN_NAME'
    # Test Data
    JSON_API_DATA_LOCATION = 'JSON_API_DATA_LOCATION'

class Sources(object):
    """Sources to get the configuration variables from"""

    ENVIRON = 'environ'
