__author__ = 'mpa'

from interfaces.Checker import Checker as ABCChecker
import logging
import re

from services.DatabaseManager import DatabaseManager
from model.Entities import Topology, Service, Network, SecurityGroup, Image, Flavor, Key
from emm_exceptions.NotFoundException import NotFoundException
from emm_exceptions.InvalidInputException import InvalidInputException
from emm_exceptions.TypeErrorException import TypeErrorException
from emm_exceptions.NotDefinedException import NotDefinedException
from emm_exceptions.NotUniqueException import NotUniqueException


logger = logging.getLogger(__name__)

class CheckerDummy(ABCChecker):

    @staticmethod
    def check(action=None, alarm=None, flavor=None, image=None, key=None, network=None, policy=None, security_group=None,
              service=None, service_instance=None, service_type=None, topology=None, unit=None):
        logger.debug("CheckerDummy: Check resource.")