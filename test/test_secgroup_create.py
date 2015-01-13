import os

__author__ = 'mpa'

import httplib
import json

PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
HOST = 'localhost'

if __name__ == '__main__':
    #Establish connection to EMM
    connection = httplib.HTTPConnection('%s:8090' % HOST)
    headers = {'Content-type': 'application/json'}


    new_secgroup = {}
    new_secgroup["name"] = "secgroup"
    new_secgroup['rules'] = []
    new_secgroup['rules'].append({'name':'tcp', 'remote_ip_prefix':'0.0.0.0/0', 'protocol':'tcp', 'port_range_min':1, 'port_range_max':65535})
    new_secgroup['rules'].append({'name':'udp', 'remote_ip_prefix':'0.0.0.0/0', 'protocol':'udp', 'port_range_min':1, 'port_range_max':65535})

    new_secgroup_json = json.dumps(new_secgroup)

    print new_secgroup_json
    connection.request('POST', '/secgroups', new_secgroup_json, headers)
    response = connection.getresponse()
    resp = (response.read())

    print 'response: %s' % resp