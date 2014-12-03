# Copyright 2014 Technische Universitaet Berlin
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from sqlalchemy import Column, Integer, String, PickleType, Enum, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import logging


conf = {
    'db_password': '*4root#',
    'db_username': 'root',
    'db_url': 'localhost',
    'db_name': 'nubomedia'
}
Base = declarative_base()
engine = create_engine('mysql://' + conf['db_username'] + ':' + conf['db_password'] + '@' + conf['db_url'] + '/' + conf['db_name'], echo=True)

__author__ = 'giuseppe'

state = ('Error', 'Initialised', 'Installed', 'Deployed', 'Active', 'Started', 'Stopped');

logger = logging.getLogger('EMMLogger')


class State:
    ref_state = state


class Service(Base):
    __tablename__ = 'Service'

    id = Column(Integer, primary_key=True)
    service_type = Column(String(50), unique=True)
    image = Column(String(50))
    flavor = Column(String(50))
    size = Column(PickleType)
    security_groups = relationship('SecurityGroup')
    type = Column(String(50))
    config = Column(PickleType)

    __mapper_args__ = {
        'polymorphic_identity': 'Service',
        'polymorphic_on': type
    }

    def __init__(self, service_type=None, config={}, image=None, flavor=None, size=None, security_groups=[]):
        self.service_type = service_type
        self.config = config
        self.image = image
        self.flavor = flavor
        self.size = size
        self.security_groups = security_groups


    def __str__(self):
        t = ""
        t += '<Service>['
        #t += 'id: %s, ' % (self.id)
        #t += 'name: %s, ' % (self.name)
        t += 'service_type: %s, ' % (self.service_type)
        t += 'image: %s, ' % (self.image)
        t += 'flavor: %s, ' % (self.flavor)
        t += 'size: %s, ' % (self.size)
        t += 'config: %s, ' % (self.config)
        t += 'security_groups: ['
        if self.security_groups:
            t += '%s' % self.security_groups[0].__str__()
            for security_group in self.security_groups[1:]:
                t += ', %s' % security_group.__str__()
        else:
            t += 'None'
        t += ']'
        #t += 'policies: ['
        #if self.policies:
        #    t += '%s' % self.policies[0].__str__()
        #    for policy in self.policies[1:]:
        #        t += ', %s' % policy.__str__()
        #else:
        #    t += 'None'
        #t += ']]'
        return t


class SecurityGroup(Base):
    __tablename__ = 'SecurityGroup'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    rules = relationship('Rule', cascade="all, delete, delete-orphan")
    service_id = Column(Integer, ForeignKey('Service.id'))

    def __init__(self, name, rules=[]):
        self.name = name
        self.rules = rules

    def __str__(self):
        t = ""
        t += '<SecurityGroup>['
        t += 'id: %s, ' % self.id
        t += 'name: %s, ' % self.name
        t += 'Rules: ['
        if self.rules:
            t += '%s' % self.rules[0].__str__()
            for rule in self.rules[1:]:
                t += ', %s' % rule.__str__()
        else:
            t += 'None'
        t += ']]'
        return t


class ServiceInstance(Service):
    __tablename__ = 'ServiceInstance'

    id = Column(Integer, ForeignKey('Service.id'), primary_key=True)
    name = Column(String(50), unique=True)
    state = Column('State', Enum(*state))
    units = relationship('Unit', cascade="all, delete, delete-orphan")
    requirements = relationship('Requirement', cascade="all, delete, delete-orphan")
    topology_id = Column(Integer, ForeignKey('Topology.id'))
    user_data = Column(String(250))
    policies = relationship('Policy', cascade="all, delete, delete-orphan")
    security_groups = relationship('SecurityGroup', cascade="all, delete, delete-orphan")
    # requirement_id = Column(Integer, ForeignKey('Requirement.id'))

    __mapper_args__ = {
        'polymorphic_identity': 'ServiceInstance',
    }

    def __init__(self, name=None, service_type=None, config={}, image=None, flavor=None, size=None, security_groups=[],
                 policies=[], state=None, units=[], requirements=[], user_data=None):
        self.name = name
        self.state = state
        self.units = units
        self.requirements = requirements
        self.user_data = user_data
        self.policies = policies
        self.service_type = service_type
        self.config = config
        self.image = image
        self.flavor = flavor
        self.size = size
        self.security_groups = security_groups

    def add_unit(self, unit):
        self.units.append(unit)

    def remove_unit(self, id):
        for unit in self.units:
            if unit.id == id:
                self.units.remove(unit)

    def __str__(self):
        t = ""
        t += '<ServiceInstance>['
        t += 'name: %s, ' % (self.name)
        t += 'state: %s, ' % (self.state)
        t += 'units: ['
        if self.units:
            t += '%s' % self.units[0].__str__()
            for unit in self.units[1:]:
                t += ', %s' % unit.__str__()
        else:
            t += 'None'
        t += '], '
        t += 'requirements: ['
        if self.requirements:
            t += '%s' % self.requirements[0].__str__()
            for requirement in self.requirements[1:]:
                t += ', %s' % requirement.__str__()
        else:
            t += 'None'
        t += '], '
        #t += "-user_data: %s, " % self.user_data
        t += 'service: %s' % Service.__str__(self)
        t += '], '
        t += 'policies: ['
        if self.policies:
            t += '%s' % self.policies[0].__str__()
            for policy in self.policies[1:]:
                t += ', %s' % policy.__str__()
        else:
            t += 'None'
        t += ']]'
        return t


class Topology(Base):
    __tablename__ = 'Topology'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    state = Column('State', Enum(*state))
    service_instances = relationship('ServiceInstance', cascade="all, delete, delete-orphan")

    def __init__(self, name=None, state=None, service_instances=[]):
        self.name = name
        self.state = state
        self.service_instances = service_instances

    def __str__(self):
        t = ""
        t += '<Topology>['
        #t += 'id: %s, ' % (self.id)
        t += 'name: %s, ' % (self.name)
        t += 'Service Instance Components: ['
        if self.service_instances:
            t += '%s' % self.service_instances[0].__str__()
            for si in self.service_instances[1:]:
                t += ', %s' % si.__str__()
        else:
            t += 'None'
        t += ']]'
        return t


class Unit(Base):
    __tablename__ = 'Unit'

    id = Column(Integer, primary_key=True)
    hostname = Column(String(20))
    ext_id = Column(String(30))
    ips = Column(PickleType)
    networks = Column(PickleType)
    state = Column('State', Enum(*state))
    service_instance_id = Column(Integer, ForeignKey('ServiceInstance.id'))
    requirement_id = Column(Integer, ForeignKey('Requirement.id'))

    def __init__(self, hostname, state, ext_id=None, ips={}, networks={}):
        self.hostname = hostname
        self.state = state
        self.ext_id = ext_id
        self.ips = ips
        self.networks = networks


class Relation(object):
    pass


class Rule(Base):
    __tablename__ = 'Rule'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    remote_ip_prefix = Column(String(50))
    protocol = Column(String(50))
    port_range_min = Column(Integer)
    port_range_max = Column(Integer)
    security_group_id = Column(Integer, ForeignKey('SecurityGroup.id'))

    def __init__(self, name, remote_ip_prefix, protocol, port_range_min=None, port_range_max=None):
        self.name = name
        self.remote_ip_prefix = remote_ip_prefix
        self.protocol = protocol
        self.port_range_min = port_range_min
        self.port_range_max = port_range_max

    def __str__(self):
        t = ""
        t += '<Rule>['
        t += 'id:%s, ' % (self.id)
        t += 'name:%s, ' % (self.name)
        t += 'remote_ip_prefix:%s, ' % (self.remote_ip_prefix)
        t += 'protocol:%s, ' % (self.protocol)
        t += 'port_range_min:%s, ' % (self.port_range_min)
        t += 'port_range_max:%s]' % (self.port_range_max)
        return t


class Policy(Base):
    __tablename__ = 'Policy'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    period = Column(Integer)
    alarm = relationship('Alarm', uselist=False, cascade='all, delete, delete-orphan')
    action = relationship('Action', uselist=False, cascade='all, delete, delete-orphan')

    service_instance_id = Column(Integer, ForeignKey('ServiceInstance.id'))

    def __init__(self, name, period, alarm, action):
        self.name = name
        self.period = period
        self.alarm = alarm
        self.action = action

    def __str__(self):
        t = ""
        t += '<Policy>['
        t += 'id:%s, ' % (self.id)
        t += 'name:%s, ' % (self.name)
        # t += 'Alarms: ['
        # if self.alarms:
        #     t += '%s' % self.alarms[0].__str__()
        #     for alarm in self.alarms[1:]:
        #         t += ', %s' % alarm.__str__()
        # else:
        #     t += 'None'
        # t += '], '
        # t += 'Actions: ['
        # if self.actions:
        #     t += '%s' % self.actions[0].__str__()
        #     for action in self.actions[1:]:
        #         t += '%s' % action.__str__()
        # else:
        #     t += 'None'
        t += ']]'
        return t


class Alarm(Base):
    __tablename__ = 'Alarm'
    id = Column(Integer, primary_key=True)
    meter_name = Column(String(50))
    statistic = Column(String(50))
    # period = Column(Integer)
    evaluation_periods = Column(Integer)
    threshold = Column(Integer)
    # repeat_actions = Column(String(50))
    comparison_operator = Column(String(5))

    policy_id = Column(Integer, ForeignKey('Policy.id'))

    def __init__(self, meter_name, statistic, period, evaluation_periods, threshold, repeat_actions,
                 comparison_operator):
        self.meter_name = meter_name
        self.statistic = statistic
        self.period = period
        self.evaluation_periods = evaluation_periods
        self.threshold = threshold
        self.repeat_actions = repeat_actions
        self.comparison_operator = comparison_operator

    def __str__(self):
        t = ""
        t += '<Alarm>['
        t += 'id:%s, ' % (self.id)
        t += 'meter_name:%s, ' % (self.meter_name)
        t += 'statistic:%s, ' % (self.statistic)
        t += 'period:%s, ' % (self.period)
        t += 'evaluation_periods:%s, ' % (self.evaluation_periods)
        t += 'threshold:%s, ' % (self.threshold)
        t += 'repeat_actions:%s, ' % (self.repeat_actions)
        t += 'comparision_operator:%s]' % (self.comparison_operator)
        return t


class Action(Base):
    __tablename__ = 'Action'
    id = Column(Integer, primary_key=True)
    adjustment_type = Column(String(50))
    cooldown = Column(Integer)
    scaling_adjustment = Column(Integer)

    policy_id = Column(Integer, ForeignKey('Policy.id'))

    def __init__(self, adjustment_type, cooldown, scaling_adjustment):
        self.adjustment_type = adjustment_type
        self.cooldown = cooldown
        self.scaling_adjustment = scaling_adjustment

    def __str__(self):
        t = ""
        t += '<Action>['
        t += 'id:%s, ' % (self.id)
        t += 'adjustment_type:%s, ' % (self.adjustment_type)
        t += 'cooldown:%s, ' % (self.cooldown)
        t += 'scaling_adjustment:%s]' % (self.scaling_adjustment)
        return t


class Requirement(Base):

    __tablename__ = 'Requirement'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    parameter = Column(String(50))
    # from who
    source = Column(String(50))
    service_instance_id = Column(Integer, ForeignKey('ServiceInstance.id'))

    def __init__(self, name, parameter, source):
        self.name = name
        self.parameter = parameter
        self.source = source

    def __str__(self):
        t = ""
        t += '<Requirement>['
        t += 'name:%s, ' % self.name
        t += 'parameter:%s, ' % self.parameter
        t += 'source:%s, ' % self.source
        #t += 'source_units:%s]' % self.source_units
        return t


class Configuration(Base):
    __tablename__ = 'Configuration'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    props = Column(PickleType)

    # def __init__(self, name=None, props={}):
    #     self.name = name
    #     self.props = props


"""
Drop all and recreate
"""
logger.debug("drop and create tables")
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)