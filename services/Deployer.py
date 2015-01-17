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

from interfaces.Deployer import Deployer as ABCDeployer
from services.DatabaseManager import DatabaseManager
from services import TemplateManager
from util.FactoryAgent import FactoryAgent
from util.SysUtil import SysUtil
from clients.heat import Client as HeatClient


__author__ = 'mpa'

logger = logging.getLogger('EMMLogger')


class Deployer(ABCDeployer):
    def __init__(self):
        self.heatclient = HeatClient()
        conf = SysUtil().get_sys_conf()
        logger.debug("Get runtime agent: " + conf['runtime_agent'])
        self.runtime_agent = FactoryAgent().get_agent(conf['runtime_agent'])
        #self.register_agent = FactoryAgent().get_agent(file_name=conf['register_agent_file'],
        #                                              class_name=conf['register_agent_class'])
        self.db = DatabaseManager()

    def deploy(self, topology):
        logger.debug("Start Deploying topology %s" % topology.name)
        _name = topology.ext_name
        _template = TemplateManager.get_template(topology)
        logger.debug("Stack name: %s" % _name)
        logger.debug("Template: %s" % _template)
        try:
            stack_details = self.heatclient.deploy(name=_name, template=_template)
            logger.debug("stack details after deploy: %s" % stack_details)
            topology.ext_id = stack_details['stack']['id']
            logger.debug("stack id: %s" % topology.ext_id)
        except Exception, msg:
            logger.error(msg)
            topology.state = 'ERROR'
            topology.ext_id = None
            return topology
        logger.debug("Starting RuntimeAgent for topology %s." % topology.id)
        self.runtime_agent.start(topology)
        #self.register_agent.start()
        return topology

    def dispose(self, topology):
        # checker_thread = self.checker_thread
        # logger.debug("Get RuntimeAgent for topology %s" % topology.id)
        # runtime_agent = self.runtime_agents.get(topology.id)
        #logger.debug("Got RuntimeAgent: %s" % self.runtime_agent)
        stack_details = None
        topology.state = 'DELETING'
        self.db.update(topology)
        if self.runtime_agent:
            self.runtime_agent.stop(topology.id)
            try:
                stack_details = self.heatclient.delete(topology.ext_id)
            except Exception, msg:
                logger.error(msg)
                topology.state = 'ERROR'
                #topology.ext_id = None
            topology.state = 'DELETED'
            self.db.update(topology)
            logger.debug("stack details after delete: %s" % stack_details)
        return stack_details

