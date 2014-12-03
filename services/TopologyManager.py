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

__author__ = 'mpa'

from util.TopologyManager import TopologyManager as ABCTopologyManager
import uuid
from model.Entities import Topology, Unit, Requirement, Alarm, Action, Policy, SecurityGroup, Rule, Service, ServiceInstance, State
from services.DatabaseManager import DatabaseManager

class TopologyManager(ABCTopologyManager):

    def __init__(self):
        self.topology = None
        self.db = DatabaseManager()

    def create(self, config):
        ###Topology arguments
        print config
        name = config.get('name')
        #id = uuid.uuid4()
        service_instance_components = []
        #security_groups = []

        print "parse Topology: %s" % name

        ###Parse all service instances described in config file
        sis_config = config.get('service_instances')
        for si_config in sis_config:
            si_args = {}
            #si_args['id'] = uuid.uuid4()
            si_args['state'] = 'Initialised'
            for si_item in si_config:
                #print "key: %s ; value: %s" % (si_item, si_config[si_item])
                if si_item == "name":
                    si_args['name'] = si_config.get(si_item)
                    print "parse service instance: %s" % si_args['name']
                elif si_item == "service_type":
                    si_args['service_type'] = si_config.get(si_item)
                elif si_item == "image":
                    si_args['image'] = si_config.get(si_item)
                elif si_item == "flavor":
                    si_args['flavor'] = si_config.get(si_item)
                elif si_item == "size":
                    si_args['size'] = si_config.get(si_item)
                elif si_item == "config":
                    si_args['config'] = si_config.get(si_item)
                elif si_item == "policies":
                    policies = []
                    _policies = si_config.get(si_item)
                    for _policy in _policies:
                        #_new_id = uuid.uuid4()
                        _new_name = None
                        _new_alarms = []
                        _new_actions = []
                        for _po_item in _policy:
                            if _po_item == "name":
                                _new_name = _policy.get(_po_item)
                            elif _po_item == "alarms":
                                _alarms = _policy.get(_po_item)
                                for _alarm in _alarms:
                                    #_id = uuid.uuid4()
                                    _new_alarm = Alarm(**_alarm)
                                    _new_alarms.append(_new_alarm)
                            elif _po_item == "actions":
                                _actions = _policy.get(_po_item)
                                for _action in _actions:
                                    #_id = uuid.uuid4()
                                    _new_action = Action(**_action)
                                    _new_actions.append(_new_action)
                        _new_policy = Policy(name = _new_name, alarms=_new_alarms, actions=_new_actions)
                        policies.append(_new_policy)
                    si_args['policies'] = policies
                elif si_item == "requirements":
                   requirements = []
                   for _req in si_config.get(si_item):
                       #_id = uuid.uuid4()
                       _req_args = _req
                       requirement = Requirement(**_req_args)
                       requirements.append(requirement)
                   si_args['requirements'] = requirements
                elif si_item == "user_data":
                    si_args['user_data'] = si_config.get(si_item)
                elif si_item == "security_groups":
                    secgroups = []
                    for _secgroup_id in si_config.get(si_item):
                        _secgroup = self.db.get_by_id(SecurityGroup, _secgroup_id)
                        secgroups.append(_secgroup)
                    si_args['security_groups'] = secgroups

            ###Initialise Units
            units = []
            unit_number = si_config.get('size').get('def') or 1
            for i in range(1,unit_number+1):
                #_uid = uuid.uuid4()
                _uhostname = '%s_%s' % (si_config.get('config').get('hostname') or si_config.get('name'),i)
                _new_unit = Unit(hostname=_uhostname, state='Initialised')
                units.append(_new_unit)
            si_args['units'] = units
            ###Initialise Service Instance
            new_service_instance_component = ServiceInstance(**si_args)
            service_instance_components.append(new_service_instance_component)

        # ###Update service_instance.requirements for existing units
        # for service_instance_component in service_instance_components:
        #     for requirement in service_instance_component.requirements:
        #         _source = service_instance_component #requirement.source
        #         for _service_instance_component in service_instance_components:
        #             if _service_instance_component.name == _source:
        #                 requirement.source = _service_instance_component

        #db.persist(self.topology)

        #logger.debug(self.topology.id)


        ###Parse all Security Groups described in config file
        #secgroups_config = config.get('security_groups')
        #security_groups = []
        #for secgroup_config in secgroups_config:
        #    security_group = None
        #    _sec_id = uuid.uuid4()
        #    _sec_name = None
        #    _sec_rules = []
        #    for secgroup_item in secgroup_config:
        #        if secgroup_item == "name":
        #            _sec_name = secgroup_config.get(secgroup_item)
        #            print "parse SecurityGroup: %s" % _sec_name
        #        elif secgroup_item == "rules":
        #            new_sec_rules = secgroup_config.get(secgroup_item)
        #            for new_sec_rule in new_sec_rules:
        #                _sec_rule_id = uuid.uuid4()
        #                _sec_rule_args = new_sec_rule
        #                _sec_rule = Rule(id=_sec_rule_id, **_sec_rule_args)
        #                _sec_rules.append(_sec_rule)
        #    security_group = SecurityGroup(id=_sec_id, name=_sec_name, rules=_sec_rules)
        #    security_groups.append(security_group)

        ###Initialise Topology
        #self.topology = Topology(name=name, id=id, service_instance_components=service_instance_components, security_groups=security_groups)
        self.topology = Topology(name=name, service_instances=service_instance_components)
        db = DatabaseManager()
        #print Service(service_instance_components[0])
        print self.topology
        #db.persist(Service(service_instance_components[0]))
        db.persist(self.topology)
        return self.topology

    def update(self):
        pass


