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


from abc import ABCMeta, abstractmethod


class Deployer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        """
        Initializes a new Deployer.
        :param tenant_name:
        :param username:
        :param password:
        :param auth_url:
        :return:
        """
        print "ABC - Deployer.__init__()"

    @abstractmethod
    def deploy(self, topology):
        """
        Deploys a new stack.
        :return:
        """
        print "ABC - Deployer.deploy()"

    @abstractmethod
    def provision(self, topology, dnsaas):
        """
        Provision the instantiated stack.
        :return:
        """
        print "ABC - Deployer.provision()"

    @abstractmethod
    def dispose(self):
        """
        Disposes an existing stack.
        :return:
        """
        print "ABC - Deployer.dispose()"

    @abstractmethod
    def details(self):
        """
        Disposes an existing stack.
        :return:
        """
        print "ABC - Deployer.details()"