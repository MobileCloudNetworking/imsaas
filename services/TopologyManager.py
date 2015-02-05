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
from emm_exceptions.NotDefinedException import NotDefinedException
from emm_exceptions.InvalidInputException import InvalidInputException
from interfaces.TopologyManager import TopologyManager as ABCTopologyManager
from services.DatabaseManager import DatabaseManager
from model.Entities import Topology, Unit, Requirement, Alarm, Action, Policy, SecurityGroup, Service, ServiceInstance, Command, \
    Network, Network_Instance, NetworkInstance_SecurityGroup, Flavor, Image, Key
from copy import deepcopy as copy
from util.FactoryAgent import FactoryAgent
from util.SysUtil import SysUtil as sys_util

__author__ = 'mpa'

logger = logging.getLogger(__name__)


class TopologyManager(ABCTopologyManager):

    def __init__(self):
        self.db = DatabaseManager()

    def create(self, config):
        ###Topology arguments
        top_name = config.get('name')
        top_state = 'DEFINED'
        top_service_instances = []
        logger.debug("Parse Topology \"%s\"" % top_name)
        ###Parse all service instances described in config file
        sis_config = config.get('service_instances')
        for si_config in sis_config:
            si_args = {}
            si_args['state'] = 'DEFINED'
            service = None
            if si_config.get('service_type'):
                service_type = si_config.get('service_type')
                logger.debug('Fetching service of service_type \"%s\"' % service_type)
                service_list = self.db.get_by_service_type(Service, service_type)
                if len(service_list) == 1:
                    service = service_list[0]
                    logger.debug('Service \"%s\" is available.' % service)
                    si_args['service_type'] = service.service_type
                    si_args['image'] = service.image
                    si_args['flavor'] = service.flavor
                    si_args['configuration'] = service.configuration
                    si_args['key'] = service.key
                    si_args['size'] = service.size
                    si_args['requirements'] = []
                    for requirement in service.requirements:
                        func = Requirement.__init__
                        needed_parameters = func.func_code.co_varnames[1:func.func_code.co_argcount]
                        args = {}
                        for param in needed_parameters:
                            args[param] = requirement.__dict__.get(param)
                        new_requirement = Requirement(**args)
                        si_args['requirements'].append(new_requirement)
                    si_args['networks'] = []
                    for network in service.networks:
                        func = Network_Instance.__init__
                        needed_parameters = func.func_code.co_varnames[1:func.func_code.co_argcount]
                        args = {}
                        for param in needed_parameters:
                            args[param] = network.__dict__.get(param)
                        new_network = Network_Instance(**args)
                        si_args['networks'].append(new_network)
                    si_args['user_data'] = []
                    for command in service.user_data:
                        func = Command.__init__
                        needed_parameters = func.func_code.co_varnames[1:func.func_code.co_argcount]
                        args = {}
                        for param in needed_parameters:
                            args[param] = command.__dict__.get(param)
                        new_command = Command(**args)
                        si_args['user_data'].append(new_command)
                else:
                    raise NotFoundException('service_type:\"%s\" is not available.' % service_type)
            else:
                raise NotDefinedException("service_type is not defined.")
            for si_item in si_config:
                if si_item == "name":
                    si_args['name'] = si_config.get(si_item)
                    logger.debug("Parsing service instance \"%s\"" % si_args['name'])
                elif si_item == "service_type":
                    si_args['service_type'] = si_config.get(si_item)
                elif si_item == "image":
                    image_name = si_config.get(si_item)
                    image_list = self.db.get_by_name(Image, image_name)
                    if len(image_list) == 1:
                        image = image_list[0]
                        si_args['image'] = image
                    else:
                        raise NotFoundException('image:\"%s\" is not available.' % image_name)
                elif si_item == "flavor":
                    flavor_name = si_config.get(si_item)
                    flavor_list = self.db.get_by_name(Flavor, flavor_name)
                    if len(flavor_list) == 1:
                        flavor = flavor_list[0]
                        si_args['flavor'] = flavor
                    else:
                        raise NotFoundException('flavor:\"%s\" is not available.' % flavor_name)
                elif si_item == "key":
                    key_name = si_config.get(si_item)
                    key_list = self.db.get_by_name(Key, key_name)
                    if len(key_list) == 1:
                        key = key_list[0]
                        si_args['key'] = key
                    else:
                        raise NotFoundException('key:\"%s\" is not available.' % key_name)
                elif si_item == "size":
                    si_args['size'].update(si_config.get(si_item))
                elif si_item == "networks":
                    networks = []
                    _networks = si_config.get(si_item)
                    logger.debug("Fetch SecurityGroups for networks %s." % _networks)
                    for _net_inst in _networks:
                        secgroups = []
                        for _secgroup_name in _net_inst.get('security_groups'):
                            lst = self.db.get_by_name(SecurityGroup, _secgroup_name)
                            if len(lst) > 0:
                                _secgroup = lst[0]
                            else:
                                raise NotFoundException('SecurityGroup:\"%s\" is not available.'  % _secgroup_name)
                            secgroups.append(_secgroup)
                        _net_inst['security_groups'] = secgroups
                        networks.append(Network_Instance(**_net_inst))
                    si_args['networks'] = networks
                elif si_item == "configuration":
                    for key in si_config.get(si_item).keys():
                        if key in service.configuration.keys():
                            si_args['configuration'][key] = si_config.get(si_item).get(key)
                elif si_item == "policies":
                    policies = []
                    _policies = si_config.get(si_item)
                    for _policy in _policies:
                        _new_policy_args = {}
                        for _po_item in _policy:
                            if _po_item == "name":
                                _new_policy_args.update({'name':_policy.get(_po_item)})
                            elif _po_item == "period":
                                _new_policy_args.update({'period':_policy.get(_po_item)})
                            elif _po_item == "alarm":
                                _new_alarm_args = _policy.get(_po_item)
                                _new_alarm = Alarm(**_new_alarm_args)
                                _new_policy_args.update({'alarm':_new_alarm})
                            elif _po_item == "action":
                                _new_action_args = _policy.get(_po_item)
                                _new_action = Action(**_new_action_args)
                                _new_policy_args.update({'action':_new_action})
                        try:
                            _new_policy = Policy(**_new_policy_args)
                        except TypeError:
                            raise InvalidInputException()
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
                else:
                    raise InvalidInputException("parameter \"%s\" is not provided by Services." % si_config.get(si_item))

            ###Initialise Units
            units = []
            unit_number = si_args.get('size').get('def') or 1
            for i in range(1,unit_number+1):
                _hostname = '%s-%s' % (si_args.get('name'),i)
                _new_unit = Unit(hostname=_hostname, state='DEFINED')
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

    def update(self, new_topology, old_topology):
        conf = sys_util().get_sys_conf()
        db = FactoryAgent().get_agent(conf['database_manager'])
        updated_topology = old_topology
        updated_topology.name = new_topology.name
        #check for additional service instances and add them to the list of new instances
        appended_service_instances = []
        for new_service_instance in new_topology.service_instances:
            is_found = False
            for updated_service_instance in updated_topology.service_instances:
                if new_service_instance.name == updated_service_instance.name:
                    is_found = True
                    break
            if not is_found:
                appended_service_instances.append(new_service_instance)
        #check for removed service instances and add it to the list of removed instances
        removed_service_instances = []
        for updated_service_instance in updated_topology.service_instances:
            is_found = False
            for new_service_instance in new_topology.service_instances:
                if new_service_instance.name == updated_service_instance.name:
                    is_found = True
                    break
            if not is_found:
                removed_service_instances.append(updated_service_instance)
        #remove removed service instances
        for removed_service_instance in removed_service_instances:
            updated_topology.service_instances.remove(removed_service_instance)
            logger.debug('Removed ServiceInstance \"%s\" from Topology \"%s\".' % (removed_service_instance.name, updated_topology.name))
        #append additional service instances
        for appended_service_instance in appended_service_instances:
            appended_service_instance.topology_id = updated_topology.id
            updated_topology.service_instances.append(appended_service_instance)
            if appended_service_instance.policies is not None:
                for policy in appended_service_instance.policies:
                    db.persist(policy)
            db.persist(appended_service_instance)
            logger.debug('Appended ServiceInstance \"%s\" to Topology \"%s\".' % (appended_service_instance.name, updated_topology.name))
        #Update all values for each service instance
        for updated_service_instance in updated_topology.service_instances:
            for new_service_instance in new_topology.service_instances:
                if updated_service_instance.name == new_service_instance.name:
                    updated_service_instance.size = new_service_instance.size
                    updated_service_instance.configuration = new_service_instance.configuration
                    updated_service_instance.policies = new_service_instance.policies
                    #updated_service_instance.service_type = new_service_instance.service_type
                    if new_service_instance.service_type and updated_service_instance.service_type != new_service_instance.service_type:
                        logger.warning("Cannot update service_type for %s->%s. Not Implemented." % (updated_topology.name, updated_service_instance.name))
                    #updated_service_instance.flavor = new_service_instance.flavor
                    if new_service_instance.flavor and updated_service_instance.flavor.name != new_service_instance.flavor.name:
                        logger.warning("Cannot update flavor for %s->%s. Not Implemented." % (updated_topology.name, updated_service_instance.name))
                    #updated_service_instance.image = new_service_instance.image
                    if new_service_instance.image and updated_service_instance.image.name != new_service_instance.image.name:
                        logger.warning("Cannot update image for %s->%s. Not Implemented." % (updated_topology.name, updated_service_instance.name))
                    #updated_service_instance.networks = new_service_instance.networks
                    if new_service_instance.networks is not None:
                        logger.warning("Cannot update networks for %s->%s. Not Implemented." % (updated_topology.name, updated_service_instance.name))
                    #updated_service_instance.requirements = new_service_instance.requirements
                    if new_service_instance.requirements is not None:
                        logger.warning("Cannot update networks for %s->%s. Not Implemented." % (updated_topology.name, updated_service_instance.name))
                    #updated_service_instance.user_data = new_service_instance.user_data
                    if new_service_instance.user_data is not None:
                        logger.warning("Cannot update user_data for %s->%s. Not Implemented." % (updated_topology.name, updated_service_instance.name))
                    if new_service_instance.key and updated_service_instance.key.name != new_service_instance.key.name:
                        logger.warning("Cannot update key for %s->%s without replacement." % (updated_topology.name, updated_service_instance.name))
        #Add or remove units according to minimal or maximal size
        for updated_service_instance in updated_topology.service_instances:
            if updated_service_instance not in appended_service_instances:
                if len(updated_service_instance.units) < updated_service_instance.size.get('min'):
                    for i in range(updated_service_instance.size.get('min') - len(updated_service_instance.units)):
                        _hostname = '%s-%s' % (
                            updated_service_instance.name, str(len(updated_service_instance.units) + 1))
                        _state = 'DEFINED'
                        new_unit = Unit(hostname=_hostname, state=_state)
                        new_unit.service_instance_id = updated_service_instance.id
                        updated_service_instance.units.append(new_unit)
                        db.persist(new_unit)
                if len(updated_service_instance.units) > updated_service_instance.size.get('max'):
                    for i in range(len(updated_service_instance.units) - updated_service_instance.size.get('max')):
                        removed_unit = updated_service_instance.units.pop(len(updated_service_instance.units) - 1)
                        db.remove(removed_unit)
        return updated_topology

    def dynamic_create(self, dict):
        logger.debug(dict)
        t = Topology(**dict)
        logger.debug(t.__dict__)
        return t

    def get_attrs(self,_class):
        return [k for k in dir(_class) if not k.startswith('__') ]