TARGET_CABINET = 'g13-27'
MERCURY = 'http://mercury.iad3.kir.kickstart.rackspace.com:9005'
TARGET_QUERY = {'interfaces.lldp': {'$regex': '{}.*'.format(TARGET_CABINET)}}


