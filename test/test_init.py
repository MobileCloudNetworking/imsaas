#!/usr/bin/python

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

    connection.request('POST', '/init', None, headers)
    response = connection.getresponse()
    resp = (response.read())

    print 'response: %s' % resp


