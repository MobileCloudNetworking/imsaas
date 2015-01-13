__author__ = 'mpa'

import json
import os

if __name__ == '__main__':
    config_file = open(os.path.join('/net/u/mpa/project/services/emm-generic/data/json_file/topologies', 'topology.json'))
    config_json = config_file.read()
    config_dict = json.loads(config_json)

    networks = config_dict.get('service_instances')[0].get('config').get('networks')

    #id = for network in networks: network.get('id') if network.get('type') == 'pubic_net'
    id = [network.get('id') for network in networks if network.get('type') == 'public_net'].pop()
    print id
    print networks

    print config_dict
