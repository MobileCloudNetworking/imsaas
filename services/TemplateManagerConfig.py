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
from services.DatabaseManager import DatabaseManager
from model.Entities import ServiceInstance, Network
from util import SysUtil
from util.SysUtil import to_json
import yaml


__author__ = 'mpa'

logger = logging.getLogger('EMMLogger')

class TemplateManagerConfig(object):

    @staticmethod
    def get_template(topology):
        #name = topology.name
        _template = {}
        _template['heat_template_version'] = '2013-05-23'
        _resources = {}
        _outputs = {}
        logger.debug("create Template for Topology: %s" % topology.name)

        db = DatabaseManager()

        for service_instance in topology.service_instances:
            _software_config = None
            #Create SoftwareConfig for user_data
            if service_instance.user_data:
                _inputs = []
                if service_instance.requirements:
                    for requirement in service_instance.requirements:
                        _inputs.append(requirement.name)
                _software_config = SoftwareConfig(name='%s-SoftwareConfig' % service_instance.name, config=service_instance.user_data, group=service_instance.name, inputs=_inputs)

            for unit in service_instance.units:
                #Create input values for user_data for SoftwareDeployment
                if service_instance.requirements or service_instance.user_data:
                    _input_values = {}
                    for requirement in service_instance.requirements:
                        try:
                            source_service_instances = db.get_by_name(ServiceInstance,requirement.source)
                        except:
                            logger.debug('ERROR: Entry %s was not found in Table ServiceInstance' % requirement.source)
                            raise
                        source_units = []
                        if source_service_instances:
                            source_service_instance = source_service_instances[0]
                            source_units = source_service_instance.units
                            logger.debug(source_units)
                            if source_units:
                                if requirement.parameter == 'private_ip' or requirement.parameter == 'public_ip':
                                    #Get requested network specified in the requirement
                                    _networks = [network for network in source_service_instance.networks if network.name == requirement.obj_name ]
                                    _network = None
                                    if _networks:
                                        _network_id = _networks[0].private_net
                                    else:
                                        logger.debug('ERROR: obj_name %s was not found in networks of ServiceInstance %s' % (requirement.obj_name,source_service_instance))
                                        raise
                                    #Get network name of the specified network id
                                    _network_names = [network.name for network in db.get_all(Network) if network.ext_id == _network_id]
                                    _network_name = None
                                    if _network_names:
                                        _network_name = _network_names[0]
                                    else:
                                        logger.debug('ERROR: Cannot find network with id %s in Table Network' % _network_id)
                                    if requirement.parameter == "private_ip":
                                        ip_number = 0
                                    elif requirement.parameter == "public_ip":
                                        ip_number = 1
                                    #Create the variable
                                    _param_params = {}
                                    _first_unit = source_units[0]
                                    _param_template = '$%s' % _first_unit.hostname
                                    _param_params['$%s' % _first_unit.hostname] = {'get_attr': [_first_unit.hostname, 'networks', _network_name, ip_number]}
                                    for source_unit in source_units[1:]:
                                        _param_template += ';$%s' % source_unit.hostname
                                        _param_params['$%s' % source_unit.hostname] = {'get_attr': [source_unit.hostname, 'networks', _network_name, ip_number]}
                                param = {}
                                param[requirement.name] = {}
                                param[requirement.name]['str_replace'] = {}
                                param[requirement.name]['str_replace']['template'] = _param_template
                                param[requirement.name]['str_replace']['params'] = _param_params
                                _input_values.update(param)
                            else:
                                logger.debug('ERROR: Units for ServiceInstance %s were not found.' % requirement.source)
                                raise Exception
                        else:
                            logger.debug('ERROR: ServiceInstance %s was not found' % requirement.source)
                            raise Exception
                    _software_deployment = SoftwareDeployment(name='%s-SoftwareDeployment' % unit.hostname, config=_software_config, server=unit, input_values=_input_values)
                    _resources.update(_software_deployment.dump_to_dict())

                #Create Ports and floating IPs for this unit
                _ports = []
                _floating_ips = []
                if service_instance.networks:
                    i=1
                    for network in service_instance.networks:
                        ###Creating Port for this service instance
                        _new_port = None
                        #prepare port args for this service instance
                        _port_args = {}
                        _port_args['name'] = '%s-port-%s' % (unit.hostname, i)
                        _port_args['private_net_id'] = network.private_net
                        _port_args['private_subnet_id'] = network.private_subnet
                        _port_args['fixed_ip'] = network.fixed_ip
                        if network.security_groups:
                            _port_args['security_groups'] = network.security_groups
                        _new_port = Port(**_port_args)
                        _ports.append(_new_port)
                        if network.public_net:
                            _new_floating_ip_args = {}
                            _new_floating_ip_args['name'] = '%s-floating_ip-%s' % (unit.hostname, i)
                            _new_floating_ip_args['floating_network_id'] = network.public_net
                            _new_floating_ip_args['port'] = _new_port.name
                            _new_floating_ip = FloatingIP(**_new_floating_ip_args)
                            _floating_ips.append(_new_floating_ip)
                        ###Adding Security Groups
                        for _security_group in network.security_groups:
                            _new_name=_security_group.name
                            _new_rules=[]
                            _rules=_security_group.rules
                            for _rule in _rules:
                                _name = _rule.name
                                _remote_ip_prefix = _rule.remote_ip_prefix
                                _protocol = _rule.protocol
                                _port_range_max = int(_rule.port_range_max) if _rule.port_range_max else None
                                _port_range_min = int(_rule.port_range_min) if _rule.port_range_min else None
                                _new_rule = Rule(_name, _remote_ip_prefix, _protocol, _port_range_max, _port_range_min)
                                _new_rules.append(_new_rule)
                            _new_security_group = SecurityGroup(name=_new_name, rules=_new_rules)
                            _resources.update(_new_security_group.dump_to_dict())
                        i += 1

                ###Create Server for this service instance
                _new_server = None
                #prepare server args
                _server_args = {}
                _server_args['name'] = "%s" % unit.hostname
                _server_args['hostname'] = "%s" % unit.hostname
                _server_args['flavor'] = service_instance.flavor.name
                _server_args['image'] = service_instance.image.name
                _server_args['key_name'] = service_instance.key.name
                _server_args['network_ports'] = _ports
                _server_args['user_data'] = service_instance.user_data
                _server_args['requirements'] = service_instance.requirements
                _new_server = Server(**_server_args)

                _resources.update(_new_server.dump_to_dict())

                if _software_config:
                    _resources.update(_software_config.dump_to_dict())
                if _ports:
                    for _port in _ports:
                        _resources.update(_port.dump_to_dict())
                if _floating_ips:
                    for _floating_ip in _floating_ips:
                        _resources.update(_floating_ip.dump_to_dict())
        print _resources
        _template['resources'] = _resources

        ###Output section###
        db = DatabaseManager()
        for service_instance in topology.service_instances:
            for network_instance in service_instance.networks:
                if network_instance.public_net:
                    _public_network_names = [_network.name for _network in db.get_all(Network) if
                                             _network.ext_id == network_instance.public_net]
                    _public_network_name = None
                    if _public_network_names:
                        _public_network_name = _public_network_names[0]
                    else:
                        logger.debug('ERROR: Cannot find network with id %s in Table Network' % network_instance.public_net)
                if network_instance.private_net:
                    _private_network_names = [_network.name for _network in db.get_all(Network) if
                                              _network.ext_id == network_instance.private_net]
                    _private_network_name = None
                    if _private_network_names:
                        _private_network_name = _private_network_names[0]
                    else:
                        logger.debug('ERROR: Cannot find network with id %s in Table Network' % network_instance.net)
                for unit in service_instance.units:
                    if network_instance.public_net and _public_network_name:
                        output = {}
                        output['value'] = {'get_attr': [unit.hostname, 'networks', _private_network_name, 1]}
                        output['description'] = 'Public IP of %s.' % unit.hostname
                        _outputs['mcn.endpoint.%s' % unit.hostname] = output
                    elif network_instance.private_net and _private_network_name:
                        output = {}
                        output['value'] = {'get_attr': [unit.hostname, 'networks', _private_network_name, 0]}
                        output['description'] = 'Private IP of %s.' % unit.hostname
                        _outputs['mcn.endpoint.%s' % unit.hostname] = output
        _template['outputs'] = _outputs

        yaml.add_representer(unicode, lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:str', value))
        yaml.add_representer(SysUtil.literal_unicode, SysUtil.literal_unicode_representer)
        logger.debug((_template))
        #logger.debug(yaml.dumps(template))
        #f = open('/net/u/mpa/tempalte_file.yaml', 'w')
        #f.write(yaml.dump(template, indent=2))
        return yaml.dump(_template)


class Server(object):
    def __init__(self, name, hostname, flavor, image, availability_zone=None, key_name = None, network_ports = [], user_data = None, requirements = []):
        ###Resource Type###
        self.type = "OS::Nova::Server"

        ###Basic parameters###
        self.name = name
        self.hostname = hostname
        self.image = image
        self.flavor = flavor
        self.key_name = key_name
        self.network_ports = network_ports
        self.user_data = user_data
        self.requirements = requirements
        self.availability_zone = availability_zone


    def dump_to_dict(self):
        resource = {}
        server_config = {}
        server_config['type'] = self.type
        properties = {}
        properties['name'] = self.name
        properties['image'] = self.image
        properties['flavor'] = self.flavor
        if self.key_name is not None: properties['key_name'] = self.key_name
        if self.availability_zone is not None: properties['availability_zone'] = self.availability_zone
        if self.network_ports is not None:
            networks = []
            logger.debug(self.network_ports)
            for network_port in self.network_ports:
                networks.append({'port': { 'get_resource' : network_port.name}})
            properties['networks'] = networks
        if self.user_data:
            properties['user_data_format'] = 'SOFTWARE_CONFIG'
        server_config['properties'] = properties
        resource[self.name] = server_config
        return resource


class Port(object):
    def __init__(self, name, private_net_id, private_subnet_id, fixed_ip=None, security_groups = []):
        self.name = name
        self.type = 'OS::Neutron::Port'
        self.private_net_id = private_net_id
        self.private_subnet_id = private_subnet_id
        self.fixed_ip = fixed_ip
        self.security_groups = security_groups

    def dump_to_dict(self):
        resource = {}
        port_config = {}
        port_config['type'] = self.type

        properties = {}
        properties['network_id'] = self.private_net_id
        
        if self.private_subnet_id or self.fixed_ip:
            properties['fixed_ips'] = []
        if self.fixed_ip:
            properties['fixed_ips'].append({'ip_address' : self.fixed_ip})
        elif self.private_subnet_id:
            properties['fixed_ips'].append({'subnet_id' : self.private_subnet_id})
        if self.security_groups:
            properties['security_groups'] = []
            for security_group in self.security_groups:
                properties['security_groups'].append({'get_resource': security_group.name})
        port_config['properties'] = properties
        resource[self.name] = port_config
        return resource


class FloatingIP(object):
    def __init__(self, name, floating_network_id, port):
        self.name = name
        self.type = 'OS::Neutron::FloatingIP'
        self.floating_network_id = floating_network_id
        self.port = port

    def dump_to_dict(self):
        resource = {}
        floating_ip_config = {}
        floating_ip_config['type'] = self.type

        properties = {}
        properties['floating_network_id'] = self.floating_network_id
        properties['port_id'] = {'get_resource': self.port}

        floating_ip_config['properties'] = properties
        resource[self.name] = floating_ip_config
        return resource


class SecurityGroup(object):
    def __init__(self, name, rules = []):
        self.name = name
        self.type = 'OS::Neutron::SecurityGroup'
        self.rules = rules

    def dump_to_dict(self):
        resource = {}
        security_group_config = {}
        security_group_config['type'] = self.type

        properties = {}
        properties['rules'] = []
        for rule in self.rules:
            properties['rules'].append(rule.dump_to_dict())

        security_group_config['properties'] = properties
        resource[self.name] = security_group_config
        return resource


class Rule(object):
    def __init__(self, name, remote_ip_prefix, protocol, port_range_max, port_range_min):
        self.name = name
        self.remote_ip_prefix = remote_ip_prefix
        self.protocol = protocol
        self.port_range_max = port_range_max
        self.port_range_min = port_range_min

    def dump_to_dict(self):
        rule_config = {}
        rule_config['remote_ip_prefix'] = self.remote_ip_prefix
        rule_config['protocol'] = self.protocol
        if self.port_range_min and self.port_range_max:
            rule_config['port_range_max'] = self.port_range_max
            rule_config['port_range_min'] = self.port_range_min
        return rule_config

class SoftwareConfig(object):
    def __init__(self, name, config=[], group=None, inputs=[], outputs=[]):
        self.name = name
        self.type = 'OS::Heat::SoftwareConfig'
        self.config = config
        self.group = "script"
        self.inputs = inputs
        self.outputs = outputs

    def dump_to_dict(self):
        resource = {}
        software_config_config = {}
        software_config_config['type'] = self.type

        properties = {}
        if self.config:
            _config = ''
            for command in self.config:
                _config += "%s\n" % command.command
            properties['config'] = SysUtil.literal_unicode((_config))
        if self.group: properties['group'] = self.group
        if self.inputs:
            _inputs = []
            for input in self.inputs:
                _inputs.append({'name':input})
            properties['inputs'] = _inputs
        if self.outputs:
            properties['outputs'] = self.outputs
        else:
            properties['outputs'] = [{'name':'result'}]
        software_config_config['properties']= properties
        resource[self.name] = software_config_config
        return resource

class SoftwareDeployment(object):
    def __init__(self, name, config=None, server=None, input_values={}):
        self.name = name
        self.type = 'OS::Heat::SoftwareDeployment'
        self.config = config
        self.server = server
        self.input_values = input_values

    def dump_to_dict(self):
        resource = {}
        software_deployment_config = {}
        software_deployment_config['type'] = self.type

        properties = {}
        if self.config: properties['config'] = {'get_resource' : self.config.name}
        if self.server: properties['server'] = {'get_resource' : self.server.hostname}
        if self.input_values: properties['input_values'] = self.input_values


        software_deployment_config['properties'] = properties
        resource[self.name] = software_deployment_config
        return resource


