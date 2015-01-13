from interfaces.MonitoringAgent import MonitoringAgent as ABCMonitoringAgent
import logging
#from clients.ceilometer import Client as CeilometerClient
import random

__author__ = 'mpa'

logger = logging.getLogger('EMMLogger')

class MonitoringAgentDummy(ABCMonitoringAgent):

    def __init__(self):
        #self.cmclient = CeilometerClient()
        logger.debug("initialised monitoring agent")

    def deploy(self, token, tenant):
        pass

    def address(self, token):
        pass

    def get_item(self, res_id, item_name, **kwargs):
        item_value = random.randint(0,100)
        return item_value

    def dispose(self, token):
        pass