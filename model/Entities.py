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
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
#    under the License.
import json
from sqlalchemy import Column, Integer, String, PickleType, Enum, ForeignKey, create_engine, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relationship
import logging


# conf = SysUtil().get_sys_conf()
Base = declarative_base()
# engine = DatabaseManager().engine


#create_engine(
#'mysql://' + conf['db_username'] + ':' + conf['db_password'] + '@' + conf['db_url'] + '/' + conf['db_name'],
#echo=False)

__author__ = 'giuseppe'

state = ('ERROR', 'DEFINED', 'DEPLOYING', 'DEPLOYED', 'INITIALISING', 'INITIALISED', 'DELETING', 'DELETED', 'UPDATING', 'UPDATED', 'STATE_NOT_IMPLEMENTED');

logger = logging.getLogger('EMMLogger')


class State:
    ref_state = state


class AbstractService(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __init__(self):
        self.service_type
        self.type
        self.image
        self.flavor
        self.size
        self.config


class Service(AbstractService, Base):
    __tablename__ = 'Service'
    id = Column(Integer, primary_key=True)
    service_type = Column(String(50), unique=True)
    image = Column(String(50))
    flavor = Column(String(50))
    size = Column(PickleType)
    config = Column(PickleType)

    def __init__(self, service_type=None, config={}, image=None, flavor=None, size=None):
        self.service_type = service_type
        self.config = config
        self.image = image
        self.flavor = flavor
        self.size = size

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
        t += ']'
        return t


class Command(Base):
    __tablename__ = 'Command'

    id = Column(Integer, primary_key=True)
    command = Column(String(256))
    service_instance_id = Column(Integer, ForeignKey('ServiceInstance.id'))

    def __init__(self, command):
        self.command = command


NetworkInstance_SecurityGroup = Table('NetworkInstance_SecurityGroup', Base.metadata,
                                      Column('Network_Instance_id', Integer, ForeignKey('Network_Instance.id')),
                                      Column('SecurityGroup_id', Integer, ForeignKey('SecurityGroup.id'))
)
NetworkInstance_SecurityGroup.__name__ = 'NetworkInstance_SecurityGroup'


class ServiceInstance(AbstractService, Base):
    __tablename__ = 'ServiceInstance'

    id = Column(Integer, primary_key=True)
    service_type = Column(String(50))
    flavor = Column(String(50))
    image = Column(String(50))
    name = Column(String(50))
    state = Column('State', Enum(*state))
    size = Column(PickleType)
    networks = relationship('Network_Instance', cascade="all, delete, delete-orphan", lazy='immediate')
    units = relationship('Unit', cascade="all, delete, delete-orphan", lazy='immediate')
    requirements = relationship('Requirement', cascade="all, delete, delete-orphan", lazy='immediate')
    topology_id = Column(Integer, ForeignKey('Topology.id'))
    user_data = relationship('Command', cascade="all, delete, delete-orphan", lazy='immediate')
    policies = relationship('Policy', cascade="all, delete, delete-orphan", lazy='immediate')
    config = Column(PickleType)


    def __init__(self, name=None, service_type=None, config={}, image=None, flavor=None, size={},
                 policies=[], state=None, units=[], requirements=[], user_data=[], networks=[]):
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
        self.networks = networks

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
        t += 'networks: ['
        if self.networks:
            t += '%s' % self.networks[0].__str__()
            for network in self.networks[1:]:
                t += ', %s' % network.__str__()
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
        #t += 'service: %s' % Service.__str__(self)
        #t += '], '
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
    ext_name = Column(String(50), unique=True)  # heat constraint
    name = Column(String(50), unique=False)
    ext_id = Column(String(50))
    state = Column('State', Enum(*state))
    service_instances = relationship('ServiceInstance', cascade="all, delete, delete-orphan", lazy='immediate')

    def __init__(self, name=None, state=None, service_instances=[], ext_id=None, ext_name=None):
        self.name = name
        self.ext_id = ext_id
        self.state = state
        self.service_instances = service_instances
        self.ext_name = ext_name

    def __str__(self):
        t = ""
        t += '<Topology>['
        t += 'id: %s, ' % self.id
        t += 'name: %s, ' % self.name
        t += 'Service Instance Components: ['
        if self.service_instances:
            t += '%s' % self.service_instances[0].__str__()
            for si in self.service_instances[1:]:
                t += ', %s' % si.__str__()
        else:
            t += 'None'
        t += ']]'
        return t


class Port(Base):
    __tablename__ = 'Port'

    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    ext_id = Column(String(50))
    mac_address = Column(String(50))
    unit_id = Column(Integer, ForeignKey('Unit.id'))
    ips = Column(PickleType)

    def __init__(self, name, ext_id=None, mac_address=None, ips={}):
        self.name = name
        self.state = state
        self.ext_id = ext_id
        self.mac_address = mac_address
        self.ips = ips

    def __str__(self):
        t = ""
        t += '<Port>['
        t += 'id: %s, ' % self.id
        t += 'name: %s, ' % self.name
        t += 'mac_address: %s, ' % self.mac_address
        t += 'ext_id: %s' % self.ext_id
        t += ']'
        return t


class Unit(Base):
    __tablename__ = 'Unit'

    id = Column(Integer, primary_key=True)
    hostname = Column(String(20))
    ext_id = Column(String(50))
    availability_zone = Column(String(50))
    ips = Column(PickleType)
    floating_ips = Column(PickleType)
    ports = relationship('Port', cascade="all, delete, delete-orphan", lazy='immediate')
    state = Column('State', Enum(*state))
    service_instance_id = Column(Integer, ForeignKey('ServiceInstance.id'))
    requirement_id = Column(Integer, ForeignKey('Requirement.id'))

    def __init__(self, hostname, state, ext_id=None, ips={}, floating_ips={}, ports = []):
        self.hostname = hostname
        self.state = state
        self.ext_id = ext_id
        self.ips = ips
        self.ports = ports
        self.floating_ips = floating_ips

    def __str__(self):
        t = ""
        t += '<Unit>['
        t += 'id: %s, ' % self.id
        t += 'hostname: %s, ' % self.hostname
        t += 'state: %s, ' % self.state
        t += 'ext_id: %s' % self.ext_id
        t += ']'
        return t

class Relation(object):
    pass


class SecurityGroup(Base):
    __tablename__ = 'SecurityGroup'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    rules = relationship('Rule', cascade="all, delete, delete-orphan", lazy='immediate')

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


class Subnet(Base):
    __tablename__ = 'Subnet'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    cidr = Column(String(50))
    network_id = Column(Integer, ForeignKey('Network.id'))
    start_ip = Column(String(50))
    end_ip = Column(String(50))
    ext_id = Column(String(50))

    def __init__(self, name, ext_id, cidr, start_ip, end_ip):
        self.name = name
        self.ext_id = ext_id
        self.end_ip = end_ip
        self.start_ip = start_ip
        self.cidr = cidr

    def __str__(self):
        t = ""
        t += '<Subnet>['
        t += 'id: %s, ' % self.id
        t += 'name: %s, ' % self.name
        t += 'ext_id: %s, ' % self.ext_id
        t += ']'
        return t


class Network(Base):
    __tablename__ = 'Network'

    id = Column(Integer, primary_key=True)
    # This colum is unique because of heat issue: in case of 2 or more Network with the same name in the HOT,
    # heat randomly pick up a Network
    name = Column(String(50), unique=True)
    public = Column(Boolean)
    subnets = relationship('Subnet', cascade="all, delete, delete-orphan", lazy='immediate')
    ext_id = Column(String(50))

    def __init__(self, name, ext_id, public=False, subnets=[]):
        self.name = name
        self.ext_id = ext_id
        self.public = public
        self.subnets = subnets

    def __str__(self):
        t = ""
        t += '<Network>['
        t += 'id: %s, ' % self.id
        t += 'name: %s, ' % self.name
        t += 'ext_id: %s, ' % self.ext_id
        t += ']'
        return t


class Network_Instance(Base):
    __tablename__ = 'Network_Instance'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    private_net = Column(String(50))
    private_subnet = Column(String(50))
    public_net = Column(String(50))
    service_instance_id = Column(Integer, ForeignKey('ServiceInstance.id'))
    security_groups = relationship('SecurityGroup', cascade="merge, expunge", secondary=NetworkInstance_SecurityGroup,
                                   lazy='immediate')

    def __init__(self, name, private_net, private_subnet=None, public_net=None, security_groups=[]):
        self.name = name
        self.private_net = private_net
        self.public_net = public_net
        self.private_subnet = private_subnet
        self.security_groups = security_groups

    def __str__(self):
        t = ""
        t += '<Network>['
        t += 'id: %s, ' % self.id
        t += 'name: %s, ' % self.name
        t += 'private_net: %s, ' % self.private_net
        t += 'private_subnet: %s, ' % self.private_subnet
        t += 'public_net: %s, ' % self.public_net
        t += ']'
        return t


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
    alarm = relationship('Alarm', uselist=False, cascade='all, delete, delete-orphan', lazy='immediate')
    action = relationship('Action', uselist=False, cascade='all, delete, delete-orphan', lazy='immediate')

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

    def __init__(self, meter_name, statistic, evaluation_periods, threshold, comparison_operator):
        self.meter_name = meter_name
        self.statistic = statistic
        #self.period = period
        self.evaluation_periods = evaluation_periods
        self.threshold = threshold
        #self.repeat_actions = repeat_actions
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
    obj_name = Column(String(50))
    service_instance_id = Column(Integer, ForeignKey('ServiceInstance.id'))

    def __init__(self, name, parameter, source, obj_name):
        self.name = name
        self.parameter = parameter
        self.source = source
        self.obj_name = obj_name

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

    def __init__(self, name=None, props={}):
        self.name = name
        self.props = props


def new_alchemy_encoder():
    _visited_objs = []

    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                # don't re-visit self
                if obj in _visited_objs:
                    return None
                _visited_objs.append(obj)

                # an SQLAlchemy class
                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                    fields[field] = obj.__getattribute__(field)
                # a json-encodable dict
                return fields

            return json.JSONEncoder.default(self, obj)

    return AlchemyEncoder


def create_tables(engine):
    """
        Drop all and recreate
        """
    logger.debug("drop and create tables")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
