import time
import yaml
from mercury.client.rpc import JobQuery


URL = 'http://localhost:9005'
YAML = '/home/jared/scratch/press_configurations/ubuntu_local.yaml'

with open(YAML) as fp:
    configuration = yaml.load(fp)

query = {}

instruction = {
    'method': 'press',
    'kwargs': {
        'configuration': configuration
    }
}


jq = JobQuery(URL, query, instruction)

jq.post_job()
time.sleep(1)
print(jq.get_status())


