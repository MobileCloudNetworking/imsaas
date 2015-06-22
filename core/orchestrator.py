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
import time

from emm_exceptions.NotFoundException import NotFoundException
from emm_exceptions.NotUniqueException import NotUniqueException
from emm_exceptions.NotDefinedException import NotDefinedException
from emm_exceptions.TypeErrorException import TypeErrorException
from emm_exceptions.InvalidInputException import InvalidInputException
from core.TopologyOrchestrator import TopologyOrchestrator

from util.FactoryAgent import FactoryAgent
from util.SysUtil import SysUtil as sys_util
from util import util as ims_util

from sdk.mcn import util

SO_DIR = os.environ.get('OPENSHIFT_REPO_DIR', '.')

logger = logging.getLogger(__name__)


topology_mapping = {
    'standalone': 'topology_ims_standalone.json',
    'test_no_services': 'topology_test_no_services.json',
    'test_dummy_topology': 'topology_dummy_service.json',
    'bern': 'topology-ims-bern.json',
    'bart': 'topology-ims-bart.json'
}

class SoExecution(object):
    """
    class docs
    """

    def __init__(self, token, tenant_name):
        """
        Constructor
        """
        # by default
        self.topology_type = "topology-ims-bern.json"
        self.token = token
        self.tenant_name = tenant_name
        self.stack_id = None
        self.maas = None
        self.location = 'bern'
        # make sure we can talk to deployer...
        logger.debug("sending request to the url %s" % os.environ['DESIGN_URI'])

        self.conf = sys_util().get_sys_conf()
        logger.debug("instantiating deployer %s" %self.conf['deployer'])
        self.deployer = None
        self.topology = None
        #self.deployer = util.get_deployer(self.token, url_type='public', tenant_name=self.tenant_name)

    def deploy(self, attributes):
        """
        Deploy method
        """
        if self.stack_id is not None:
            pass
        dnsaas = True
        parameters = {}

        # defining the location of the topology
        if 'imsaas.location' in attributes:
            self.location = parameters['location'] = os.environ['location'] = attributes['imsaas.location']
            logger.debug("location %s passed via OCCI Attribute"%self.location)

        self.deployer = FactoryAgent().get_agent(self.conf['deployer'])


        # trying to retrieve dnsaas endpoint
        # if 'mcn.endpoint.forwarder' and 'mcn.endpoint.api' in attributes:
        #     logger.debug('DNSaaS IPs were passed via OCCI attributes')
        #     parameters['dns_ip_address'] = os.environ['DNS_IP'] = attributes['mcn.endpoint.forwarder']
        #     parameters['dnsaas_ip_address'] = os.environ['DNSAAS_IP'] = attributes['mcn.endpoint.api']
        # else:
        #     try:
        #         logger.debug("DNSaaS IPs were not passed as OCCI attribute, instantiating DNSaaS")
        #         self.dnsaas = util.get_dnsaas(self.token, tenant_name=self.tenant_name)
        #         parameters['dns_ip_address'] = os.environ['DNS_IP'] = self.dnsaas.get_forwarders()
        #         parameters['dnsaas_ip_address'] = os.environ['DNSAAS_IP'] = self.dnsaas.get_address()
        #     except:
        #         logging.warning("errors while instantiating dnsaas")
        #         dnsaas = False

        dnsaas = False

        self.topology_type = topology_mapping[self.location]
        logger.info("deploying template %s" % (self.topology_type,))

        # read template...
        f = open(os.path.join(SO_DIR, 'data/topologies', self.topology_type))
        template = f.read()
        f.close()
        logger.debug("content of the topology %s" % template)

        # extracting hot template
        try:
            config = yaml.load(template)
            logger.debug(config)
        except yaml.YAMLError, exc:
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                logger.error("Error in configuration file:", exc)
                logger.error("Error position: (%s:%s)" % (mark.line + 1, mark.column + 1))
            else:
                logger.error("Error in configuration file:", exc)

        # creating the topology object
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

        # for si in self.topology.service_instances:
        #     if not dnsaas:
        #         si.user_data = si.user_data + (ims_util.get_user_data(parameters['maas_ip_address']))
        #     else:
        #         si.user_data = ims_util.get_user_data(parameters['maas_ip_address'], parameters['dnsaas_ip_address'])
        #

        # deploying the topology
        if self.stack_id is None:
            stack_details = self.deployer.deploy(self.topology)
            self.stack_id = stack_details.id
            logger.info("deployed topology with id %s" % self.stack_id)

    def provision(self, attributes):
        """
        Provision method
        """
        # provisioning the topology
        parameters = {}
        # trying to retrieve maas endpoint
        if 'mcn.endpoint.maas' in attributes:
            logger.debug("MaaS IP was passed as attribute")
            parameters['maas_ip_address'] = os.environ['ZABBIX_IP'] = attributes['mcn.endpoint.maas']
        else:
            try:
                logger.debug("Maas IP was not passed as attribute")
                self.maas = util.get_maas(self.token, tenant_name=self.tenant_name)
                parameters['maas_ip_address'] = os.environ['ZABBIX_IP'] = self.maas.get_address(self.token)
                logger.info("maas instantiated with address %s" % os.environ['ZABBIX_IP'])
            except Exception, e:
                logger.error("Problems instantiating maas")
                raise SystemError("Problems instantiating maas")

        if self.stack_id is not None:
            stack_details = self.deployer.provision(self.topology)
            self.stack_id = stack_details.id
            logger.info("deployed topology with id %s" % self.stack_id)

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
            if self.maas is not None:
                util.dispose_maas(self.token, self.maas)

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
            return 'CREATE_COMPLETE', 'N/A', ''


class ServiceOrchestrator(object):
    def __init__(self, token, tenant_name):
        os.environ['OS_AUTH_TOKEN'] = token
        self.so_e = SoExecution(token, tenant_name)





