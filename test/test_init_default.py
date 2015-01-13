import os
import httplib
import requests
import time
import json
import yaml

HOST = 'localhost'

__author__ = 'mpa'

if __name__ == '__main__':

    #Establish connection to EMM
    connection = httplib.HTTPConnection('%s:8090' % HOST)
    headers = {'Content-type': 'application/json'}

    print "=============init==============="

    connection.request('POST', '/init', None, headers)
    response = connection.getresponse()
    resp = (response.read())

    print 'response: %s' % resp

    print "=============add security group==============="

    new_secgroup = {}
    new_secgroup["name"] = "secgroup"
    new_secgroup['rules'] = []
    new_secgroup['rules'].append({'name':'tcp', 'remote_ip_prefix':'0.0.0.0/0', 'protocol':'tcp', 'port_range_min':1, 'port_range_max':65535})
    new_secgroup['rules'].append({'name':'udp', 'remote_ip_prefix':'0.0.0.0/0', 'protocol':'udp', 'port_range_min':1, 'port_range_max':65535})

    new_secgroup_json = json.dumps(new_secgroup)

    connection.request('POST', '/secgroups', new_secgroup_json, headers)
    response = connection.getresponse()
    resp = (response.read())

    print 'response: %s' % resp

    print "=============add services==============="

    new_service = {}
    new_service["service_type"] = "controller"
    new_service['image'] = "nubomedia-broker"
    new_service['flavor'] = "m1.medium"
    new_service['size'] = {'def':1, 'max':1, 'min':1}
    new_service['config'] = {'hostname':'ControlServer'}
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
    new_service['size'] = {'def':1, 'max':1, 'min':1}
    new_service['config'] = {'hostname':'BrokerServer'}
    #new_service['security_groups'] = ['1']
    new_service_json = json.dumps(new_service)

    connection.request('POST', '/services', new_service_json, headers)
    response = connection.getresponse()
    resp = (response.read())

    print 'response: %s' % resp

    new_service = {}
    new_service["service_type"] = "media_server"
    new_service['image'] = "nubomedia-broker"
    new_service['flavor'] = "m1.medium"
    new_service['size'] = {'def':3, 'max':5, 'min':1}
    new_service['config'] = {'hostname':'MediaServer'}
    #new_service['security_groups'] = ['1']
    new_service_json = json.dumps(new_service)

    connection.request('POST', '/services', new_service_json, headers)
    response = connection.getresponse()
    resp = (response.read())

    print 'response: %s' % resp
