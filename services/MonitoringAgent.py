__author__ = 'mpa'

from util.MonitoringAgent import MonitoringAgent as ABCMonitoringAgent

class MonitoringAgent(ABCMonitoringAgent):

    def __init__(self, endpoint):
        pass

    def deploy(self, token, tenant):
        pass

    def address(self, token):
        pass

    def get_item(self, res_id, item_name, **kwargs):
        pass

    def dispose(self, token):
        pass