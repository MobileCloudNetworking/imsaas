import os
from model.Entities import Service, SecurityGroup, Rule
from wsgi.application import to_json

__author__ = 'lto'

import logging
PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s_%(process)d:%(pathname)s:%(lineno)d [%(levelname)s] %(message)s',level=logging.DEBUG)
    logger = logging.getLogger("EMMLogger")
    handler = logging.FileHandler('%s/logs/%s.log' % (PATH, os.path.basename(__file__)))
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s_%(process)d:%(pathname)s:%(lineno)d [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    service_to_create = Service()
    service_to_create.service_type = 'dummy'
    service_to_create.size = "7GB"
    service_to_create.config = {
        'KEY1': 'VALUE1',
        'KEY2': 'VALUE2',
        'KEY3': 'VALUE3'
    }
    service_to_create.flavor = 'm1.small'
    service_to_create.image = 'dummy-image'
    logger.debug("\n" + to_json(service_to_create))

    logger.debug("###########################")

    r = Rule('Rule1', port_range_max=65535, port_range_min=1, protocol='tcp', remote_ip_prefix='127.0.0.1')
    sec_group = SecurityGroup('SecGroup1', rules=[r])
    logger.debug(to_json(r))
    logger.debug("\n" + to_json(sec_group))