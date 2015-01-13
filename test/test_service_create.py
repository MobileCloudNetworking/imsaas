import os
from model.Entities import SecurityGroup
from wsgi.application import to_json

__author__ = 'mpa'

import httplib
import json

PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
HOST = 'localhost'

if __name__ == '__main__':
    # Establish connection to EMM
    connection = httplib.HTTPConnection('%s:8090' % HOST)
    headers = {'Content-type': 'application/json'}

    new_service = {}
    new_service["service_type"] = "controller"
    new_service['image'] = "nubomedia-broker"
    new_service['flavor'] = "m1.medium"
    new_service['size'] = {'def': 1, 'max': 1, 'min': 1}
    new_service['config'] = {'hostname': 'ControlServer'}
    #new_service['security_groups'] = ['1']
    new_service_json = json.dumps(new_service)

    connection.request('POST', '/services', new_service_json, headers)
    response = connection.getresponse()
    resp = (response.read())

    print 'response: %s' % resp

    new_service = {}
    new_service["service_type"] = "broker"
    new_service['image'] = "nubomedia-broker"
    new_service['flavor'] = "m1.medium"
    new_service['size'] = {'def': 1, 'max': 1, 'min': 1}
    new_service['config'] = {'hostname': 'BrokerServer'}
    new_service_json = json.dumps(new_service)

    connection.request('POST', '/services', new_service_json, headers)
    response = connection.getresponse()
    resp = (response.read())

    print 'response: %s' % resp

    new_service = {}
    new_service["service_type"] = "media_server"
    new_service['image'] = "nubomedia-broker"
    new_service['flavor'] = "m1.medium"
    new_service['size'] = {'def': 3, 'max': 5, 'min': 1}
    new_service['config'] = {'hostname': 'MediaServer'}
    new_service_json = json.dumps(new_service)

    connection.request('POST', '/services', new_service_json, headers)
    response = connection.getresponse()
    resp = (response.read())

    print 'response: %s' % resp

    new_service = {}
    new_service["service_type"] = "dummy"
    new_service['image'] = "dummy-image"
    new_service['flavor'] = "m1.medium"
    new_service['size'] = {'def': 3, 'max': 5, 'min': 1}
    new_service['config'] = {'hostname': 'dummy-1'}
    new_service_json = json.dumps(new_service)

    connection.request('POST', '/services', new_service_json, headers)
    response = connection.getresponse()
    resp = (response.read())

    print 'response: %s' % resp