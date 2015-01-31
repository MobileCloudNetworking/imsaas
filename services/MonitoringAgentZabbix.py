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


import logging
import sys
from util.zabbix_api import ZabbixAPI
from clients.ceilometer import Client as CeilometerClient
from interfaces.MonitoringAgent import MonitoringAgent as ABCMonitoringAgent


__author__ = 'mpa'

logger = logging.getLogger(__name__)

class Singleton(object):
  _instance = None
  def __new__(class_, *args, **kwargs):
    if not isinstance(class_._instance, class_):
        class_._instance = object.__new__(class_, *args, **kwargs)
    return class_._instance

class MonitoringAgentZabbix(Singleton, ABCMonitoringAgent):


    def __init__(self):
        self.cmclient = CeilometerClient()
        self.zabbix = ZabbixAPI(server="http://160.85.4.45/zabbix")
        self.username = "Admin"
        self.password = "zabbix"
        logger.debug("initialised monitoring agent")
        try:
            logger.debug('*** Connecting to MaaS')
            self.zabbix.login(self.username, self.password)
            logger.debug('*** Connected to MaaS')
        except Exception as e:
            logger.error('*** Caught exception: %s: %s' % (e.__class__, e))
            sys.exit(1)

    def deploy(self, token, tenant):
        pass

    def address(self, token):
        pass

    def get_item(self, hostname, item_name, **kwargs):
        logger.debug("Monitor: request resource %s for %s" % (hostname, item_name))
        #item_value = self.cmclient.get_statitics(resource_id=res_id, meter_name=item_name, period=kwargs.get('period') or 60)

        try:
            hostid = self.zapi.host.get({"filter":{"host":hostname}})[0]["hostid"]
        except:
            print "WARNING: Hostname " + hostname + " not found"
            return

        try:
            item_value = self.zapi.item.get({"output":"extend","hostids":hostid,"filter":{"key_":item_name}})[0]["lastvalue"]
        except Exception as e:
            print "ERROR: User metric not found"

        logger.debug("Monitor: received %s" % item_value)
        return item_value

    def dispose(self, token):
        pass