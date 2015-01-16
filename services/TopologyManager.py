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
import random
from emm_exceptions.NotFoundException import NotFoundException
from interfaces.TopologyManager import TopologyManager as ABCTopologyManager
from services.DatabaseManager import DatabaseManager
from model.Entities import Topology, Unit, Requirement, Alarm, Action, Policy, SecurityGroup, Service, ServiceInstance, Command, \
    Network, Network_Instance, NetworkInstance_SecurityGroup
from services.Checker import check

__author__ = 'mpa'

logger = logging.getLogger('EMMLogger')


class TopologyManager(ABCTopologyManager):

    def __init__(self):
        self.db = DatabaseManager()

    def create(self, config):
        ###Topology arguments
        top_name = config.get('name')
        top_state = 'DEFINED'
        top_service_instances = []
        logger.debug("parse Topology: %s" % top_name)
        ###Parse all service instances described in config file
        sis_config = config.get('service_instances')
        for si_config in sis_config:
            si_args = {}
            si_args['state'] = 'DEFINED'
            service_type = si_config.get('service_type')
            logger.debug('service_type: %s' % service_type)
            service = None
            if service_type:
                for serv in self.db.get_all(Service):
                    if serv.service_type == service_type:
                        service = serv
                if not service:
                    raise Exception('\"service_type:%s\" not found' % service_type)
                logger.debug('service: %s' % service)
                if service:
                    logger.debug("requested Service: %s" % service)
                    si_args['image'] = service.image
                    si_args['flavor'] = service.flavor
                    si_args['config'] = service.config
                    si_args['size'] = service.size
                else:
                    logger.error("\"service:%s\" not found in Database" % service_type)
                    raise Exception
            else:
                logger.error("\"service_type\" is not defined")
                raise Exception
            for si_item in si_config:
                if si_item == "name":
                    si_args['name'] = si_config.get(si_item)
                    logger.debug("parsing service instance: %s" % si_args['name'])
                elif si_item == "service_type":
                    si_args['service_type'] = si_config.get(si_item)
                elif si_item == "image":
                    si_args['image'] = si_config.get(si_item)
                elif si_item == "flavor":
                    si_args['flavor'] = si_config.get(si_item)
                elif si_item == "size":
                    si_args['size'].update(si_config.get(si_item))
                elif si_item == "networks":
                    networks = []
                    _networks = si_config.get(si_item)
                    logger.debug(_networks)
                    for _net_inst in _networks:
                        secgroups = []
                        for _secgroup_name in _net_inst.get('security_groups'):
                            try:
                                lst = self.db.get_by_name(SecurityGroup, _secgroup_name)
                                if len(lst) > 0:
                                    _secgroup = lst[0]
                                else:
                                    raise NotFoundException('Security group ' + _secgroup_name + " was not found")
                            except NotFoundException as e:
                                raise NotFoundException(e)
                            secgroups.append(_secgroup)
                        _net_inst['security_groups'] = secgroups
                        networks.append(Network_Instance(**_net_inst))
                    si_args['networks'] = networks
                elif si_item == "config":
                    si_args['config'].update(si_config.get(si_item))
                elif si_item == "policies":
                    policies = []
                    _policies = si_config.get(si_item)
                    for _policy in _policies:
                        _new_name = None
                        _new_period = None
                        _new_alarm = None
                        _new_action = None
                        for _po_item in _policy:
                            if _po_item == "name":
                                _new_name = _policy.get(_po_item)
                            elif _po_item == "period":
                                _new_period = _policy.get(_po_item)
                            elif _po_item == "alarm":
                                _new_alarm_args = _policy.get(_po_item)
                                _new_alarm = Alarm(**_new_alarm_args)
                            elif _po_item == "action":
                                _new_action_args = _policy.get(_po_item)
                                _new_action = Action(**_new_action_args)
                        _new_policy = Policy(name = _new_name, period=_new_period, alarm=_new_alarm, action=_new_action)
                        policies.append(_new_policy)
                    si_args['policies'] = policies
                elif si_item == "requirements":
                   requirements = []
                   for _req in si_config.get(si_item):
                       _req_args = _req
                       requirement = Requirement(**_req_args)
                       requirements.append(requirement)
                   si_args['requirements'] = requirements
                elif si_item == "user_data":
                    user_data = []
                    for _user_data_item in  si_config.get(si_item):
                        command = Command(_user_data_item)
                        user_data.append(command)
                    si_args['user_data'] = user_data

            ###Initialise Units
            units = []
            unit_number = si_args.get('size').get('def') or 1
            for i in range(1,unit_number+1):
                #_uid = uuid.uuid4()
                _uhostname = '%s-%s' % (si_args.get('config').get('hostname') or si_args.get('name'),i)
                _new_unit = Unit(hostname=_uhostname, state='DEFINED')
                units.append(_new_unit)
            si_args['units'] = units
            ###Initialise Service Instance
            new_service_instance = ServiceInstance(**si_args)
            ###Add the new service instance to the topology
            top_service_instances.append(new_service_instance)

        ###Initialise Topology
        ext_name = '' + top_name + '_' +str(random.randint(1000,9999))
        topology = Topology(name=top_name, state=top_state, service_instances=top_service_instances, ext_name=ext_name)
        logger.debug(topology)
        return topology

    def update(self):
        pass

    def dynamic_create(self, dict):
        logger.debug(dict)
        t = Topology(**dict)
        logger.debug(t.__dict__)
        return t

    def get_attrs(self,_class):
        return [k for k in dir(_class) if not k.startswith('__') ]