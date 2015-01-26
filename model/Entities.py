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
# under the License.
import json
from sqlalchemy import Column, Integer, String, PickleType, Enum, ForeignKey, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relationship
import logging


# conf = SysUtil().get_sys_conf()
Base = declarative_base()
# engine = DatabaseManager().engine


# create_engine(
# 'mysql://' + conf['db_username'] + ':' + conf['db_password'] + '@' + conf['db_url'] + '/' + conf['db_name'],
# echo=False)

__author__ = 'giuseppe'

state = ('ERROR', 'DEFINED', 'DEPLOYING', 'DEPLOYED', 'INITIALISING', 'INITIALISED', 'DELETING', 'DELETED', 'UPDATING',
         'UPDATED', 'STATE_NOT_IMPLEMENTED', 'STARTED')

logger = logging.getLogger(__name__)


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
    flavor = relationship('Flavor', cascade='merge', lazy='immediate')
    flavor_id = Column(Integer, ForeignKey('Flavor.id'))
    image = relationship('Image', cascade='merge', lazy='immediate')
    image_id = Column(Integer, ForeignKey('Image.id'))
    key = relationship('Key', cascade='merge', lazy='immediate')
    key_id = Column(Integer, ForeignKey('Key.id'))
    user_data = relationship('Command', cascade="all, delete-orphan", lazy='immediate')
    requirements = relationship('Requirement', cascade="all, delete-orphan", lazy='immediate')
    networks = relationship('Network_Instance', cascade="all, delete-orphan", lazy='immediate')
    size = Column(PickleType)
    version = Column(String(50))
    configuration = Column(PickleType)

    def __init__(self, service_type, image, flavor, size, version=None, user_data=[], requirements=[], networks=[], key=None, configuration={}):
        self.id = None
        self.service_type = service_type
        self.configuration = configuration
        self.image = image
        self.image_id = None
        self.flavor = flavor
        self.flavor_id = None
        self.key = key
        self.key_id = None
        self.user_data = user_data
        self.requirements = requirements
        self.networks = networks
        self.size = size
        self.version = version

    def __str__(self):
        t = ""
        t += '<Service>['
        t += 'id:%s, ' % (self.id)
        t += 'service_type:%s, ' % (self.service_type)
        t += 'version:%s, ' % (self.version)
        t += 'image:%s, ' % (self.image)
        t += 'image_id:%s, ' % (self.image_id)
        t += 'flavor:%s, ' % (self.flavor)
        t += 'flavor_id:%s, ' % (self.flavor_id)
        t += 'key:%s, ' % (self.key)
        t += 'key_id:%s, ' % (self.key_id)
        t += 'size:%s, ' % self.size
        t += 'networks:['
        if self.networks:
            t += '%s' % self.networks[0].__str__()
            for network in self.networks[1:]:
                t += ', %s' % network.__str__()
        else:
            t += 'None'
        t += '], '
        t += 'requirements:['
        if self.requirements:
            t += '%s' % self.requirements[0].__str__()
            for requirement in self.requirements[1:]:
                t += ', %s' % requirement.__str__()
        else:
            t += 'None'
        t += '], '
        t += 'user_data:['
        if self.user_data:
            t += '%s' % self.user_data[0].__str__()
            for user_data in self.user_data[1:]:
                t += ', %s' % user_data.__str__()
        else:
            t += 'None'
        t += ']'
        t += 'configuration:%s ' % (self.configuration)
        t += ']'
        return t


class Command(Base):
    __tablename__ = 'Command'

    id = Column(Integer, primary_key=True)
    command = Column(String(256))
    service_id = Column(Integer, ForeignKey('Service.id'))
    service_instance_id = Column(Integer, ForeignKey('ServiceInstance.id'), onupdate='CASCADE')

    def __init__(self, command):
        self.id = None
        self.command = command
        self.service_instance_id = None

    def __str__(self):
        t = ""
        t += '<Command>['
        t += 'id:%s, ' % (self.id)
        t += 'command:%s, ' % (self.command)
        t += 'service_id:%s, ' % (self.service_id)
        t += 'service_instance_id:%s' % (self.service_instance_id)
        t += ']'
        return t


NetworkInstance_SecurityGroup = Table('NetworkInstance_SecurityGroup', Base.metadata,
                                      Column('Network_Instance_id', Integer, ForeignKey('Network_Instance.id', onupdate='CASCADE', ondelete='SET NULL')),
                                      Column('SecurityGroup_id', Integer, ForeignKey('SecurityGroup.id', onupdate='CASCADE', ondelete='SET NULL'))
)
NetworkInstance_SecurityGroup.__name__ = 'NetworkInstance_SecurityGroup'


class ServiceInstance(AbstractService, Base):
    __tablename__ = 'ServiceInstance'

    id = Column(Integer, primary_key=True)
    topology_id = Column(Integer, ForeignKey('Topology.id'))
    networks = relationship('Network_Instance', cascade="all, delete-orphan", lazy='immediate')
    policies = relationship('Policy', cascade="all, delete-orphan", lazy='immediate')
    requirements = relationship('Requirement', cascade="all, delete-orphan", lazy='immediate')
    units = relationship('Unit', cascade="all, delete-orphan", lazy='immediate')
    user_data = relationship('Command', cascade="all, delete-orphan", lazy='immediate')
    configuration = Column(PickleType)
    flavor_id = Column(Integer, ForeignKey('Flavor.id'))
    flavor = relationship('Flavor', cascade='merge', lazy='immediate')
    image_id = Column(Integer, ForeignKey('Image.id'))
    image = relationship('Image', cascade='merge', lazy='immediate')
    key_id = Column(Integer, ForeignKey('Key.id'))
    key = relationship('Key', cascade='merge', lazy='immediate')
    name = Column(String(50))
    service_type = Column(String(50))
    size = Column(PickleType)
    state = Column('State', Enum(*state))


    def __init__(self, name, service_type, state, image, flavor, size, key=None,
                 policies=[], units=[], requirements=[], user_data=[], networks=[], configuration={}):
        self.id = None
        self.topology_id = None
        self.configuration = configuration
        self.image = image
        self.image_id = None
        self.flavor = flavor
        self.flavor_id = None
        self.key = key
        self.key_id = None
        self.name = name
        self.networks = networks
        self.policies = policies
        self.requirements = requirements
        self.service_type = service_type
        self.size = size
        self.state = state
        self.units = units
        self.user_data = user_data


    def __str__(self):
        t = ""
        t += '<ServiceInstance>['
        t += 'id:%s, ' % (self.id)
        t += 'topology_id:%s, ' % (self.topology_id)
        t += 'name:%s, ' % (self.name)
        t += 'service_type:%s, ' % (self.service_type)
        t += 'state: %s, ' % (self.state)
        t += 'configuration:%s, ' % (self.configuration)
        t += 'image:%s, ' % (self.image)
        t += 'image_id:%s, ' % (self.image_id)
        t += 'flavor:%s, ' % (self.flavor)
        t += 'flavor_id:%s, ' % (self.flavor_id)
        t += 'key:%s, ' % (self.key)
        t += 'key_id:%s, ' % (self.key_id)
        t += 'networks:['
        if self.networks:
            t += '%s' % self.networks[0].__str__()
            for network in self.networks[1:]:
                t += ', %s' % network.__str__()
        else:
            t += 'None'
        t += '], '
        t += 'policies:['
        if self.policies:
            t += '%s' % self.policies[0].__str__()
            for policy in self.policies[1:]:
                t += ', %s' % policy.__str__()
        else:
            t += 'None'
        t += '], '
        t += 'requirements:['
        if self.requirements:
            t += '%s' % self.requirements[0].__str__()
            for requirement in self.requirements[1:]:
                t += ', %s' % requirement.__str__()
        else:
            t += 'None'
        t += '], '
        t += 'size:%s, ' % self.size
        t += 'units:['
        if self.units:
            t += '%s' % self.units[0].__str__()
            for unit in self.units[1:]:
                t += ', %s' % unit.__str__()
        else:
            t += 'None'
        t += '], '
        t += 'user_data:['
        if self.user_data:
            t += '%s' % self.user_data[0].__str__()
            for user_data in self.user_data[1:]:
                t += ', %s' % user_data.__str__()
        else:
            t += 'None'
        t += ']'
        t += ']'
        return t


class Topology(Base):
    __tablename__ = 'Topology'

    id = Column(Integer, primary_key=True)
    ext_name = Column(String(50), unique=True)  # heat constraint
    name = Column(String(50), unique=False)
    ext_id = Column(String(50))
    state = Column('State', Enum(*state))
    service_instances = relationship('ServiceInstance', cascade="all, delete, delete-orphan", lazy='immediate')

    def __init__(self, name, state, service_instances=[], ext_id=None, ext_name=None):
        self.id = None
        self.name = name
        self.ext_id = ext_id
        self.state = state
        self.service_instances = service_instances
        self.ext_name = ext_name

    def __str__(self):
        t = ""
        t += '<Topology>['
        t += 'id:%s, ' % self.id
        t += 'name:%s, ' % self.name
        t += 'ext_id:%s, ' % self.ext_id
        t += 'ext_name:%s, ' % self.ext_name
        t += 'state %s, ' % self.state
        t += 'service_instance_components['
        if self.service_instances:
            t += '%s' % self.service_instances[0].__str__()
            for si in self.service_instances[1:]:
                t += ', %s' % si.__str__()
        else:
            t += 'None'
        t += ']'
        t += ']'
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
        self.id = None
        self.unit_id = None
        self.name = name
        self.ext_id = ext_id
        self.mac_address = mac_address
        self.ips = ips

    def __str__(self):
        t = ""
        t += '<Port>['
        t += 'id:%s, ' % self.id
        t += 'unit_id:%s, ' % self.unit_id
        t += 'name:%s, ' % self.name
        t += 'mac_address:%s, ' % self.mac_address
        t += 'ext_id:%s' % self.ext_id
        t += ']'
        return t


class Unit(Base):
    __tablename__ = 'Unit'

    id = Column(Integer, primary_key=True)
    hostname = Column(String(20))
    ext_id = Column(String(50))
    availability_zone = Column(String(50))
    ws = Column(String(100))
    ips = Column(PickleType)
    floating_ips = Column(PickleType)
    ports = relationship('Port', cascade="all, delete, delete-orphan", lazy='immediate')
    state = Column('State', Enum(*state))
    service_instance_id = Column(Integer, ForeignKey('ServiceInstance.id'))
    requirement_id = Column(Integer, ForeignKey('Requirement.id'))

    def __init__(self, hostname, state, ext_id=None, ips={}, floating_ips={}, ports=[]):
        self.id = None
        self.requirement_id = None
        self.hostname = hostname
        self.state = state
        self.ext_id = ext_id
        self.ips = ips
        self.ports = ports
        self.floating_ips = floating_ips
        self.availability_zone = None
        self.ws = None

    def __str__(self):
        t = ""
        t += '<Unit>['
        t += 'id:%s, ' % self.id
        t += 'hostname:%s, ' % self.hostname
        t += 'state:%s, ' % self.state
        t += 'requirement_id:%s, ' % self.requirement_id
        t += 'ext_id:%s, ' % self.ext_id
        t += 'ips:%s, ' % self.ips
        t += 'floating_ips:%s, ' % self.floating_ips
        t += 'ws:%s, ' % self.ws
        t += 'availability_zone:%s, ' % self.availability_zone
        t += 'ports:['
        if self.ports:
            t += '%s' % self.ports[0].__str__()
            for port in self.ports[1:]:
                t += ', %s' % port.__str__()
        else:
            t += 'None'
        t += ']'
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
        self.id = None
        self.name = name
        self.rules = rules

    def __str__(self):
        t = ""
        t += '<SecurityGroup>['
        t += 'id:%s, ' % self.id
        t += 'name:%s, ' % self.name
        t += 'Rules:['
        if self.rules:
            t += '%s' % self.rules[0].__str__()
            for rule in self.rules[1:]:
                t += ', %s' % rule.__str__()
        else:
            t += 'None'
        t += ']'
        t += ']'
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
        self.id = None
        self.network_id = None
        self.name = name
        self.ext_id = ext_id
        self.end_ip = end_ip
        self.start_ip = start_ip
        self.cidr = cidr

    def __str__(self):
        t = ""
        t += '<Subnet>['
        t += 'id:%s, ' % self.id
        t += 'name:%s, ' % self.name
        t += 'ext_id:%s, ' % self.ext_id
        t += 'network_id:%s, ' % self.network_id
        t += 'cidr:%s, ' % self.cidr
        t += 'start_ip:%s, ' % self.start_ip
        t += 'end_ip:%s, ' % self.end_ip
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
        self.id = None
        self.name = name
        self.ext_id = ext_id
        self.public = public
        self.subnets = subnets

    def __str__(self):
        t = ""
        t += '<Network>['
        t += 'id:%s, ' % self.id
        t += 'name:%s, ' % self.name
        t += 'ext_id:%s, ' % self.ext_id
        t += 'public:%s, ' % self.public
        t += 'subnets:['
        if self.subnets:
            t += '%s' % self.subnets[0].__str__()
            for subnet in self.subnets[1:]:
                t += ', %s' % subnet.__str__()
        else:
            t += 'None'
        t += ']'
        t += ']'
        return t


class Key(Base):
    __tablename__ = "Key"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    def __init__(self, name):
        self.id = None
        self.name = name

    def __str__(self):
        t = ""
        t += '<Key>['
        t += 'id:%s, ' % self.id
        t += 'name:%s' % self.name
        t += ']'
        return t


class Flavor(Base):
    __tablename__ = "Flavor"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    ram = Column(String(50))
    vcpus = Column(String(50))

    def __init__(self, name, ram, vcpus):
        self.id = None
        self.name = name
        self.ram = ram
        self.vcpus = vcpus

    def __str__(self):
        t = ""
        t += '<Flavor>['
        t += 'id: %s, ' % self.id
        t += 'name: %s, ' % self.name
        t += 'ram: %s, ' % self.ram
        t += 'vcpus: %s' % self.vcpus
        t += ']'
        return t


class Image(Base):
    __tablename__ = "Image"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    ext_id = Column(String(50))
    status = Column(String(50))
    created = Column(String(50))
    updated = Column(String(50))

    def __init__(self, name, ext_id, status, created, updated):
        self.id = None
        self.name = name
        self.ext_id = ext_id
        self.status = status
        self.created = created
        self.updated = updated

    def __str__(self):
        t = ""
        t += '<Image>['
        t += 'id:%s, ' % self.id
        t += 'name:%s, ' % self.name
        t += 'ext_id:%s, ' % self.ext_id
        t += 'status:%s, ' % self.status
        t += 'created:%s, ' % self.created
        t += 'updated:%s' % self.updated
        t += ']'
        return t


class Quotas(Base):
    __tablename__ = "Quotas"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    instances = Column(Integer)
    cores = Column(Integer)
    ram = Column(Integer)
    floating_ips = Column(Integer)
    fixed_ips = Column(Integer)
    metadata_items = Column(Integer)
    injected_files = Column(Integer)
    injected_file_content_bytes = Column(Integer)
    injected_file_path_bytes = Column(Integer)
    key_pairs = Column(Integer)
    security_groups = Column(Integer)
    security_group_rules = Column(Integer)
    server_groups = Column(Integer)
    server_group_members = Column(Integer)

    def __init__(self, id, instances, cores, ram, floating_ips, fixed_ips, metadata_items, injected_files,
                 injected_file_content_bytes, injected_file_path_bytes, key_pairs, security_groups,
                 security_group_rules, server_groups=None, server_group_members=None):
        self.id = None
        self.tenant_id = id
        self.instances = instances
        self.cores = cores
        self.ram = ram
        self.floating_ips = floating_ips
        self.fixed_ips = fixed_ips
        self.metadata_items = metadata_items
        self.injected_files = injected_files
        self.injected_file_content_bytes = injected_file_content_bytes
        self.injected_file_path_bytes = injected_file_path_bytes
        self.key_pairs = key_pairs
        self.security_groups = security_groups
        self.security_group_rules = security_group_rules
        self.server_groups = server_groups
        self.server_group_members = server_group_members

    def __str__(self):
        t = ""
        t += '<Quotas>['
        t += 'id:%s, ' % self.id
        t += 'tenant_id:%s, ' % self.tenant_id
        t += 'instances:%s, ' % self.instances
        t += 'cores:%s, ' % self.cores
        t += 'ram:%s, ' % self.ram
        t += 'floating_ips:%s, ' % self.floating_ips
        t += 'fixed_ips:%s, ' % self.fixed_ips
        t += 'metadata_items:%s, ' % self.metadata_items
        t += 'injected_files:%s, ' % self.injected_files
        t += 'injected_file_content_bytes:%s, ' % self.injected_file_content_bytes
        t += 'injected_file_path_bytes:%s, ' % self.injected_file_path_bytes
        t += 'key_pairs:%s, ' % self.key_pairs
        t += 'security_groups:%s, ' % self.security_groups
        t += 'security_group_rules:%s, ' % self.security_group_rules
        t += 'server_groups:%s, ' % self.server_groups
        t += 'server_group_members:%s' % self.server_group_members
        t += ']'
        return t


class Network_Instance(Base):
    __tablename__ = 'Network_Instance'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    private_net = Column(String(50))
    private_subnet = Column(String(50))
    public_net = Column(String(50))
    fixed_ip = Column(String(50))
    service_id = Column(Integer, ForeignKey('Service.id'))
    service_instance_id = Column(Integer, ForeignKey('ServiceInstance.id'))
    security_groups = relationship('SecurityGroup', cascade="merge, expunge", secondary=NetworkInstance_SecurityGroup,
                                   lazy='immediate')

    def __init__(self, name, private_net, private_subnet=None, public_net=None, fixed_ip=None, security_groups=[]):
        self.id = None
        self.name = name
        self.private_net = private_net
        self.public_net = public_net
        self.private_subnet = private_subnet
        self.fixed_ip = fixed_ip
        self.security_groups = security_groups

    def __str__(self):
        t = ""
        t += '<Network>['
        t += 'id:%s, ' % self.id
        t += 'name:%s, ' % self.name
        t += 'private_net:%s, ' % self.private_net
        t += 'private_subnet:%s, ' % self.private_subnet
        t += 'public_net:%s, ' % self.public_net
        t += 'fixed_ip:%s, ' % self.fixed_ip
        t += 'security_groups:['
        if self.security_groups:
            t += '%s' % self.security_groups[0].__str__()
            for security_group in self.security_groups[1:]:
                t += ', %s' % security_group.__str__()
        else:
            t += 'None'
        t += ']'
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
        self.id = None
        self.security_group_id = None
        self.name = name
        self.remote_ip_prefix = remote_ip_prefix
        self.protocol = protocol
        self.port_range_min = port_range_min
        self.port_range_max = port_range_max

    def __str__(self):
        t = ""
        t += '<Rule>['
        t += 'id:%s, ' % (self.id)
        t += 'security_group_id:%s, ' % (self.security_group_id)
        t += 'name:%s, ' % (self.name)
        t += 'remote_ip_prefix:%s, ' % (self.remote_ip_prefix)
        t += 'protocol:%s, ' % (self.protocol)
        t += 'port_range_min:%s, ' % (self.port_range_min)
        t += 'port_range_max:%s' % (self.port_range_max)
        t += ']'
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
        self.id = None
        self.name = name
        self.period = period
        self.alarm = alarm
        self.action = action

    def __str__(self):
        t = ""
        t += '<Policy>['
        t += 'id:%s, ' % (self.id)
        t += 'name:%s, ' % (self.name)
        t += 'alarm:%s, ' % (self.alarm.__str__())
        t += 'action:%s, ' % (self.action.__str__())
        t += ']'
        return t


class Alarm(Base):
    __tablename__ = 'Alarm'
    id = Column(Integer, primary_key=True)
    meter_name = Column(String(50))
    statistic = Column(String(50))
    evaluation_periods = Column(Integer)
    threshold = Column(Integer)
    comparison_operator = Column(String(5))

    policy_id = Column(Integer, ForeignKey('Policy.id'))

    def __init__(self, meter_name, statistic, evaluation_periods, threshold, comparison_operator):
        self.id = None
        self.meter_name = meter_name
        self.statistic = statistic
        self.evaluation_periods = evaluation_periods
        self.threshold = threshold
        self.comparison_operator = comparison_operator

    def __str__(self):
        t = ""
        t += '<Alarm>['
        t += 'id:%s, ' % (self.id)
        t += 'meter_name:%s, ' % (self.meter_name)
        t += 'statistic:%s, ' % (self.statistic)
        t += 'evaluation_periods:%s, ' % (self.evaluation_periods)
        t += 'threshold:%s, ' % (self.threshold)
        t += 'comparision_operator:%s' % (self.comparison_operator)
        t += ']'
        return t


class Action(Base):
    __tablename__ = 'Action'
    id = Column(Integer, primary_key=True)
    adjustment_type = Column(String(50))
    cooldown = Column(Integer)
    scaling_adjustment = Column(Integer)

    policy_id = Column(Integer, ForeignKey('Policy.id'))

    def __init__(self, adjustment_type, cooldown, scaling_adjustment):
        self.id = None
        self.adjustment_type = adjustment_type
        self.cooldown = cooldown
        self.scaling_adjustment = scaling_adjustment

    def __str__(self):
        t = ""
        t += '<Action>['
        t += 'id:%s, ' % (self.id)
        t += 'adjustment_type:%s, ' % (self.adjustment_type)
        t += 'cooldown:%s, ' % (self.cooldown)
        t += 'scaling_adjustment:%s' % (self.scaling_adjustment)
        t += ']'
        return t


class Requirement(Base):
    __tablename__ = 'Requirement'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    parameter = Column(String(50))
    # from who
    source = Column(String(50))
    obj_name = Column(String(50))
    service_id = Column(Integer, ForeignKey('Service.id'))
    service_instance_id = Column(Integer, ForeignKey('ServiceInstance.id'), onupdate='CASCADE')

    def __init__(self, name, parameter, source, obj_name):
        self.id = None
        self.name = name
        self.parameter = parameter
        self.source = source
        self.obj_name = obj_name

    def __str__(self):
        t = ""
        t += '<Requirement>['
        t += 'id:%s, ' % self.id
        t += 'name:%s, ' % self.name
        t += 'service_id:%s, ' % self.service_id
        t += 'service_instance_id:%s, ' % self.service_instance_id
        t += 'parameter:%s, ' % self.parameter
        t += 'source:%s, ' % self.source
        t += 'obj_name:%s' % self.obj_name
        t += ']'
        return t


class Configuration(Base):
    __tablename__ = 'Configuration'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    props = Column(PickleType)

    def __init__(self, name=None, props={}):
        self.id = None
        self.name = name
        self.props = props

    def __str__(self):
        t = ""
        t += '<Configuration>['
        t += 'id:%s, ' % self.id
        t += 'name:%s, ' % self.name
        t += 'props:%s' % self.props
        t += ']'
        return t


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
