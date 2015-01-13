"""
This script has the task of providing some entries in the DB in order to easily use the test of the EMM
"""
import logging
import os
from services.DatabaseManager import DatabaseManager
from model import Entities
from model.Entities import SecurityGroup, Rule, Service, Configuration
from util.FactoryAgent import FactoryAgent
from util.SysUtil import SysUtil

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

