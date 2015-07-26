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

from util.FactoryAgent import FactoryAgent
from util.SysUtil import SysUtil as sys_util
from sdk.mcn import util
# from sm.so import service_orchestrator
# from sm.so.service_orchestrator import LOG

logger = logging.getLogger(__name__)

SO_DIR = os.environ.get('OPENSHIFT_REPO_DIR', '.')

TOPOLOGY_MAPPING = {
    'standalone': {'topology_type': 'topology_ims_standalone.json', 'dnsaas': 'False'},
    'test_no_services': {'topology_type': 'topology_test_no_services.json','dnsaas': 'False'},
    'test_dummy_topology': {'topology_type':'topology_dummy_service.json','dnsaas': 'False'},
    'bern': {'topology_type':'topology-ims-bern.json','dnsaas': 'False'},
    'bart': {'topology_type': 'topology-ims-bart.json','dnsaas': 'False'},
    'bern-no-dns': {'topology_type': 'topology-ims-bern-no-dns.json', 'dnsaas': 'True'},
}


class SoExecution():
    """
    class docs
    """

    def __init__(self, token, tenant_name, location=None):
        """
        Constructor
        """
        # by default
        self.token = token
        self.tenant_name = tenant_name
        self.stack_id = None
        self.maas = None
        self.dnsaas = None
        if location is None:
            self.location = 'bern'
        self.conf = sys_util().get_sys_conf()
        self.deployer = None
        self.topology = None

    def deploy(self, attributes):
        """
        Deploy method
        """
        if self.stack_id is not None:
            pass

        self.deployer = FactoryAgent().get_agent(self.conf['deployer'])
        topology_type = TOPOLOGY_MAPPING[self.location].get('topology_type')
        logger.info("deploying template %s" % (topology_type,))
        # read template...
        f = open(os.path.join(SO_DIR, 'data/topologies', topology_type))
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
        if TOPOLOGY_MAPPING[self.location].get('dnsaas') is 'True':
            logger.debug("DNSaaS enabled")
            # trying to retrieve dnsaas endpoint
            try:
                self.dnsaas = util.get_dnsaas(self.token, tenant_name=self.tenant_name)
            dnsaas_ip = self.dnsaas.get_address()
            dnsaas_forwarders = self.dnsaas.get_forwarders()
            if dnsaas_ip is not None:
                parameters['dnsaas_ip_address'] = os.environ['DNSAAS_IP'] = dnsaas_forwarders
                logger.info("dnsaas instantiated with address %s" % dnsaas_forwarders)
            else:
                logger.error("dnsaas instantiation got some issues, "
                            "terminating the provisioning method")
                return 42
        else:
            logger.debug("DNSaaS disabled")
        # trying to retrieve maas endpoint
        if 'mcn.endpoint.maas' in attributes:
            logger.debug("MaaS IP was passed as attribute")
            parameters['maas_ip_address'] = os.environ['ZABBIX_IP'] = attributes['mcn.endpoint.maas']
        else:
            logger.debug("Maas IP was not passed as attribute")
            self.maas = util.get_maas(self.token,
                                      tenant_name=self.tenant_name)
            maas_ip = self.maas.get_address(self.token)
            if maas_ip is not None:
                parameters['maas_ip_address'] = \
                    os.environ['ZABBIX_IP'] = \
                    maas_ip
                logger.info("maas instantiated with address %s" % maas_ip)
            else:
                logger.info("maas instantiation got some issues, using "
                            "the pre-provisioned %s" %self.conf['mcn.endpoint.maas'])
                parameters['maas_ip_address'] = \
                    os.environ['ZABBIX_IP'] = \
                    self.conf['mcn.endpoint.maas']

        if self.stack_id is not None:
            stack_details = self.deployer.provision(self.topology, self.dnsaas)
            self.stack_id = stack_details.id
            logger.info("provisioned topology with id %s" % self.stack_id)

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
            if self.dnsaas is not None:
                util.dispose_dnsaas(self.token, self.dnsaas)

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


