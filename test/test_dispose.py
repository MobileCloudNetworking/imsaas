__author__ = 'mpa'

import httplib

if __name__ == '__main__':


    #Establish connection to EMM
    connection = httplib.HTTPConnection('localhost:8090')
    headers = {'Content-type': 'application/json'}

    stack_id = '1'

    connection.request('DELETE', '/topologies/%s' % stack_id, None, headers)
    response = connection.getresponse()
    resp = (response.read())

    print 'response: %s' % resp