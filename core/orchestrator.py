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
import yaml

from emm_exceptions.NotFoundException import NotFoundException
from emm_exceptions.NotUniqueException import NotUniqueException
from emm_exceptions.NotDefinedException import NotDefinedException
from emm_exceptions.TypeErrorException import TypeErrorException
from emm_exceptions.InvalidInputException import InvalidInputException
from core.TopologyOrchestrator import TopologyOrchestrator

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
        self.topology_type = "topology_test_v2.json"
        self.token = token
        self.tenant_name = tenant_name
        self.stack_id = None
        # make sure we can talk to deployer...
        logger.debug("sending request to the url %s" % os.environ['DESIGN_URI'])

        conf = sys_util().get_sys_conf()
        logger.debug("instantiating deployer %s" %conf['deployer'])
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

        logger.info("deploying template %s" % (self.topology_type,))
        # read template...
        f = open(os.path.join(SO_DIR, 'data/topologies', self.topology_type))
        self.template = f.read()
        f.close()
        logger.debug("content of the topology %s" % self.template)
        try:
            config = yaml.load(self.template)
            logger.debug(config)
        except yaml.YAMLError, exc:
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                logger.error("Error in configuration file:", exc)
                logger.error("Error position: (%s:%s)" % (mark.line + 1, mark.column + 1))
            else:
                logger.error("Error in configuration file:", exc)

        try:
            self.topology = TopologyOrchestrator.create(config)
        except NotFoundException, msg:
            logger.error(msg)
            return
        except NotUniqueException, msg:
            logger.error(msg)
            return
        except NotDefinedException, msg:
            logger.error(msg)
            return
        except InvalidInputException, msg:
            logger.error(msg)
            return
        except TypeErrorException, msg:
            logger.error(msg)
            return
        except Exception, msg:
            logger.error(msg)
            return

        if self.stack_id is None:
            stack_details = self.deployer.deploy(self.topology)
            #stack_details = self.heatclient.deploy(name="ims",template = self.template)
            self.stack_id = stack_details.id
            logger.info("deployed topology with id %s" % self.stack_id)


    def provision(self):
        """
        Provision method
        """
        pass

    def dispose(self):
        """
        Dispose method
        """
        logger.info("deleting topology with id %s " % self.stack_id)
        if self.stack_id is not None:
            topology = TopologyOrchestrator.get(self.stack_id)
            logger.debug("topology to be deleted %s " % topology)
            self.deployer.dispose(topology)
            TopologyOrchestrator.delete(topology)
            self.stack_id = None

    def state(self):
        """
        Report on state.
        """
        logger.info("retrieving state of the running stack with id %s" % self.stack_id)
        if self.stack_id is not None:
            topology = TopologyOrchestrator.get(self.stack_id)
            stk = self.deployer.details(topology.ext_id)
            res = {'state': stk['stack_status'],
               'name': stk['stack_name'],
               'id': stk['id']}
            if 'outputs' in stk:
                res['output'] = stk['outputs']
            output = ''
            try:
                output = res['output']
            except KeyError:
                pass

            logger.debug(" state %s, output %s"%(res['state'],output))
            return res['state'], str(self.stack_id), output
        else:
            return 'Unknown', 'N/A', ''


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





