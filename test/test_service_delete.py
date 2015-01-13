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


    connection.request('DELETE', '/services/1', None, headers)
    response = connection.getresponse()
    resp = (response.read())

    print 'response: %s' % resp