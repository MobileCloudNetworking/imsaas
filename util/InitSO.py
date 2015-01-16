import json
import logging
import os

from core.SecurityGroupOrchestrator import SecurityGroupOrchestrator
from core.ServiceOrchestrator import ServiceOrchestrator

PATH = os.environ.get('OPENSHIFT_REPO_DIR', '.')


__author__ = 'gca'

logger = logging.getLogger()

class InitSO:

    def __init__(self):
        self.__init_security_groups()
        self.__init_services()

    def __init_security_groups(self):
            logger.debug("=============Add SecurityGroups===============")

            ###Get the config file for testing purposes
            f = open(os.path.join('%s/data/security_group/' % PATH, 'SecurityGroup-ims.json'))
            config_file = f.read()
            f.close()
            json_file = config_file
            resp = SecurityGroupOrchestrator.create(json.loads(json_file))
            logger.debug('response: %s' % resp)

    def __init_services(self):
            for file in os.listdir(os.path.join('%s/data/services/' % PATH)):
                logger.debug("creating service from file %s" %file)
                f = open(os.path.join('%s/data/services/' % PATH, file))
                config_file = f.read()
                f.close()
                json_file = config_file
                resp = ServiceOrchestrator.create(json.loads(json_file))
                logger.debug('response: %s' % resp)

