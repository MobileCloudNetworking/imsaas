from interfaces.MonitoringAgent import MonitoringAgent as ABCMonitoringAgent
import logging
from clients.ceilometer import Client as CeilometerClient

__author__ = 'mpa'

logger = logging.getLogger('EMMLogger')


class MonitoringAgent(ABCMonitoringAgent):

    def __init__(self):
        self.cmclient = CeilometerClient()
        logger.debug("initialised monitoring agent")

    def deploy(self, token, tenant):
        pass

    def address(self, token):
        pass

    def get_item(self, res_id, item_name, **kwargs):
        logger.debug("Monitor: request resource %s for %s" % (res_id, item_name))
        item_value = self.cmclient.get_statitics(resource_id=res_id, meter_name=item_name, period=kwargs.get('period') or 60)
        logger.debug("Monitor: received %s" % item_value)
        return item_value

    def dispose(self, token):
        pass