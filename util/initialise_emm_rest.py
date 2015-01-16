__author__ = 'mpa'

import httplib
import os
import logging
import time


logger = logging.getLogger('EMMLogger')
HOST='localhost'
PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

__author__ = 'lto'

if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s_%(process)d:%(pathname)s:%(lineno)d [%(levelname)s] %(message)s',
                        level=logging.DEBUG)
    logger = logging.getLogger("EMMLogger")
    handler = logging.FileHandler('%s/logs/%s.log' % (PATH, os.path.basename(__file__)))
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s_%(process)d:%(pathname)s:%(lineno)d [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    #Establish connection to EMM
    print "=============Wait for Server==============="
    is_reachable = False
    while not is_reachable:
        try:
            connection = httplib.HTTPConnection('%s:8090' % HOST)
            headers = {'Content-type': 'application/json'}
            connection.request('GET', '/', None, headers)
            response = connection.getresponse()
            if response:
                print "Server is reachable"
                is_reachable = True
        except:
            print "Server is not reachable."
            time.sleep(2)

    #print "=============init==============="

    #connection.request('POST', '/init', None, headers)
    #response = connection.getresponse()
    #resp = (response.read())
    #print 'response: %s' % resp

    print "=============Add SecurityGroups==============="

    ###Get the config file for testing purposes
    f = open(os.path.join('%s/data/json_file/security_group/' % PATH, 'SecurityGroup-Broker.json'))
    config_file = f.read()
    f.close()
    json_file = config_file
    connection.request('POST', '/secgroups', json_file, headers)
    response = connection.getresponse()
    resp = (response.read())
    print 'response: %s' % resp

    ###Get the config file for testing purposes
    f = open(os.path.join('%s/data/json_file/security_group/' % PATH, 'SecurityGroup-Controller.json'))
    config_file = f.read()
    f.close()
    json_file = config_file
    connection.request('POST', '/secgroups', json_file, headers)
    response = connection.getresponse()
    resp = (response.read())
    print 'response: %s' % resp

    ###Get the config file for testing purposes
    f = open(os.path.join('%s/data/json_file/security_group/' % PATH, 'SecurityGroup-MediaServer.json'))
    config_file = f.read()
    f.close()
    json_file = config_file
    connection.request('POST', '/secgroups', json_file, headers)
    response = connection.getresponse()
    resp = (response.read())
    print 'response: %s' % resp

    ###Get the config file for testing purposes
    f = open(os.path.join('%s/data/json_file/security_group/' % PATH, 'SecurityGroup-TreeServer.json'))
    config_file = f.read()
    f.close()
    json_file = config_file
    connection.request('POST', '/secgroups', json_file, headers)
    response = connection.getresponse()
    resp = (response.read())
    print 'response: %s' % resp

    print "=============Add Services==============="

    f = open(os.path.join('%s/data/json_file/services/' % PATH, 'ControllerService.json'))
    config_file = f.read()
    f.close()
    json_file = config_file
    connection.request('POST', '/services', json_file, headers)
    response = connection.getresponse()
    resp = response.read()
    print 'response: %s' % resp

    f = open(os.path.join('%s/data/json_file/services/' % PATH, 'MediaService.json'))
    config_file = f.read()
    f.close()
    json_file = config_file
    connection.request('POST', '/services', json_file, headers)
    response = connection.getresponse()
    resp = (response.read())
    print 'response: %s' % resp


    f = open(os.path.join('%s/data/json_file/services/' % PATH, 'BrokerService.json'))
    config_file = f.read()
    f.close()
    json_file = (config_file)
    connection.request('POST', '/services', json_file, headers)
    response = connection.getresponse()
    resp = (response.read())
    print 'response: %s' % resp

    f = open(os.path.join('%s/data/json_file/services/' % PATH, 'TreeService.json'))
    config_file = f.read()
    f.close()
    json_file = (config_file)
    connection.request('POST', '/services', json_file, headers)
    response = connection.getresponse()
    resp = (response.read())
    print 'response: %s' % resp