__author__ = 'mpa'

import os
import httplib
import logging

PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
HOST = 'localhost'


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
    connection = httplib.HTTPConnection('%s:8090' % HOST)
    headers = {'Content-type': 'application/json'}

    ###Get the config file for testing purposes
    f = open(os.path.join('%s/data/json_file/topologies/' % PATH, 'topology_template_1.json'))
    config_file = f.read()
    logger.debug(config_file)

    connection.request('POST', '/topology', config_file, headers)
    response = connection.getresponse()
    resp = (response.read())

    logger.debug('response: %s' % resp)