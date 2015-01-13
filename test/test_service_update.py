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

    new_service = {}
    new_service["service_type"] = "media_server_new"
    #new_service['image'] = "nubomedia-broker"
    #new_service['flavor'] = "m1.medium"
    new_service['size'] = {'def':3, 'max':5, 'min':1}
    new_service['config'] = {'hostname':'MediaServer'}
    #new_service['security_groups'] = ['1']
    new_service_json = json.dumps(new_service)

    connection.request('PUT', '/services/1', new_service_json, headers)
    response = connection.getresponse()
    resp = (response.read())

    print 'response: %s' % resp