# Copyright 2014 Technische Universitaet Berlin
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


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