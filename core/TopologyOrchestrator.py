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

from emm_exceptions import NotFoundException
from model.Entities import Topology
from services.DatabaseManager import DatabaseManager
from util.FactoryAgent import FactoryAgent
from util.SysUtil import SysUtil as sys_util

__author__ = 'lto'


class TopologyOrchestrator:

    def __init__(self):
        pass

    @classmethod
    def delete(cls, topology):
        db = DatabaseManager()
        db.remove(topology)
        return topology


    @classmethod
    def get(cls, id):
        db = DatabaseManager()
        try:
            topology = db.get_by_id(Topology, id)
        except NotFoundException as e:
            raise e
        return topology

    @classmethod
    def get_all(cls):
        return DatabaseManager().get_all(Topology)

    @classmethod
    def create(cls, topology_args):
        try:
            conf = sys_util().get_sys_conf()
            topology_manager = FactoryAgent().get_agent(conf['topology_manager'])
            topology = topology_manager.create(topology_args)
            checker = FactoryAgent().get_agent(conf['checker'])
            checker.check(topology=topology)
            db = DatabaseManager()
            db.persist(topology)
            #db.update(topology)
        except Exception, msg:
            raise
        return topology

