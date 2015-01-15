# Copyright 2014 Technische Universitaet Berlin
# Copyright 2014 Zuercher Hochschule fuer Angewandte Wissenschaften
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
__author__ = 'giuseppe'

import os
import logging



from sdk.mcn import util
from util.FactoryAgent import FactoryAgent
from util.SysUtil import SysUtil as sys_util
from clients.heat import Client as HeatClient


SO_DIR = os.environ.get('OPENSHIFT_REPO_DIR', '.')

logger = logging.getLogger("IMSSO")



class SoExecution(object):
    """
    class docs
    """
    def __init__(self, token, tenant_name):
        """
        Constructor
        """
        self.topology_type = "test.yaml"
        self.token = token
        self.tenant_name = tenant_name
        self.stack_id = None
        # make sure we can talk to deployer...
        logger.debug("sending request to the url %s" %os.environ['DESIGN_URI'])
        self.heatclient = HeatClient()

        conf = sys_util().get_sys_conf()
        self.deployer = FactoryAgent().get_agent(conf['deployer'])

        #self.deployer = util.get_deployer(self.token, url_type='public', tenant_name=self.tenant_name)

    def design(self):
        """
        Design method
        """


    def deploy(self, attributes):
        """
        Deploy method
        """

        parameters = {}
        parameters['maas_ip_address'] = attributes['mcn.endpoint.maas']
        try:
            self.topology_type = attributes['mcn.topology.type']
        except:
            logger.debug("parameter mcn.topology.type not available, using the standard template imsaas.yaml")

        logger.info("deploying template %s" %(self.topology_type,))
        # read template...
        f = open(os.path.join(SO_DIR, 'data', self.topology_type))
        self.template = f.read()
        f.close()

        if self.stack_id is None:
            #self.stack_id = self.deployer.deploy(self.template, self.token, parameters=parameters)
            stack_details = self.heatclient.deploy(name="ims",template = self.template)
            self.stack_id = stack_details['stack']['id']


    def provision(self):
        """
        Provision method
        """
        pass

    def dispose(self):
        """
        Dispose method
        """
        if self.stack_id is not None:
            #self.deployer.dispose(self.stack_id, self.token)
            self.heatclient.delete(self.stack_id)
            self.stack_id = None

    def state(self):
        """
        Report on state.
        """
        if self.stack_id is not None:
            tmp = self.deployer.details(self.stack_id, self.token)
            return tmp['state'], self.stack_id, tmp['output']
        else:
            return 'Unknown', 'N/A'

class SoDecision(object):
    '''
    classdocs
    '''


    def __init__(self, token, tenant):
        '''
        Constructor
        '''
        self.token = token
        self.tenant = tenant

    def run(self):
        pass


class ServiceOrchestrator(object):

    def __init__(self, token, tenant_name):
        self.so_e = SoExecution(token, tenant_name)
        self.so_d = SoDecision(token, tenant_name)





