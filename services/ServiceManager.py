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
from interfaces.ServiceManager import ServiceManager as ABCServiceManager
from services.DatabaseManager import DatabaseManager
from model.Entities import Topology, Requirement, SecurityGroup, Service, Command, Network_Instance, Flavor, Image, Key

__author__ = 'mpa'

logger = logging.getLogger(__name__)


class ServiceManager(ABCServiceManager):

    def __init__(self):
        self.db = DatabaseManager()

    def create(self, config):
        ###Service arguments
        service_type = config.get('service_type')
        logger.debug("Parse Service \"%s\"" % service_type)
        ###Parse each item described in config file
        new_service_args={}
        for service_item in config.keys():
            if service_item == "service_type":
                new_service_args['service_type'] = config.get(service_item)
            elif service_item == "image":
                image_name = config.get(service_item)
                image_list = self.db.get_by_name(Image, image_name)
                if len(image_list) == 1:
                    image = image_list[0]
                    new_service_args['image'] = image
                else:
                    raise NotFoundException('image:\"%s\" is not available.' % image_name)
            elif service_item == "flavor":
                flavor_name = config.get(service_item)
                flavor_list = self.db.get_by_name(Flavor, flavor_name)
                if len(flavor_list) == 1:
                    flavor = flavor_list[0]
                    new_service_args['flavor'] = flavor
                else:
                    raise NotFoundException('flavor:\"%s\" is not available.' % flavor_name)
            elif service_item == "key":
                key_name = config.get(service_item)
                key_list = self.db.get_by_name(Key, key_name)
                if len(key_list) == 1:
                    key = key_list[0]
                    new_service_args['key'] = key
                else:
                    raise NotFoundException('key:\"%s\" is not available.' % key_name)
            elif service_item == "size":
                new_service_args['size'] = config.get(service_item)
            elif service_item == "networks":
                networks = []
                _networks = config.get(service_item)
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
                new_service_args['networks'] = networks
            elif service_item == "configuration":
                new_service_args['configuration'] = config.get(service_item)
            elif service_item == "requirements":
               requirements = []
               for _req in config.get(service_item):
                   _req_args = _req
                   requirement = Requirement(**_req_args)
                   requirements.append(requirement)
               new_service_args['requirements'] = requirements
            elif service_item == "user_data":
                user_data = []
                for _user_data_item in  config.get(service_item):
                    command = Command(_user_data_item)
                    user_data.append(command)
                new_service_args['user_data'] = user_data
            elif service_item == "version":
                new_service_args['version'] = config.get(service_item)
            elif service_item == "adapter":
                new_service_args['adapter'] = config.get(service_item)
            else:
                raise InvalidInputException("paramter \"%s\" is not provided by Services." % config.get(service_item))


        ###Create Service
        print(new_service_args)
        new_service = Service(**new_service_args)
        logger.debug(new_service)
        return new_service

    def update(self):
        pass

    def dynamic_create(self, dict):
        logger.debug(dict)
        t = Topology(**dict)
        logger.debug(t.__dict__)
        return t

    def get_attrs(self,_class):
        return [k for k in dir(_class) if not k.startswith('__') ]

    def get_service_instance(self, _class, _name):
        return self.db.get_by_name(_class, _name)