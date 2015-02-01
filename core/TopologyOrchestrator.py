from emm_exceptions.NotFoundException import NotFoundException
from emm_exceptions.ActionInProgressException import ActionInProgressException
from model.Entities import Topology
from services.DatabaseManager import DatabaseManager
from util.FactoryAgent import FactoryAgent
from util.SysUtil import SysUtil as sys_util
import logging

__author__ = 'lto'

logger = logging.getLogger(__name__)

class TopologyOrchestrator:

    def __init__(self):
        pass

    @classmethod
    def delete(cls, topology):
        conf = sys_util().get_sys_conf()
        db = FactoryAgent().get_agent(conf['database_manager'])
        db.remove(topology)
        return topology


    @classmethod
    def get(cls, id):
        conf = sys_util().get_sys_conf()
        db = FactoryAgent().get_agent(conf['database_manager'])
        try:
            topology = db.get_by_id(Topology, id)
        except NotFoundException as e:
            raise e
        return topology

    @classmethod
    def get_all(cls):
        conf = sys_util().get_sys_conf()
        db = FactoryAgent().get_agent(conf['database_manager'])
        lst = db.get_all(Topology)
        return lst

    @classmethod
    def create(cls, topology_args):
        conf = sys_util().get_sys_conf()
        db = FactoryAgent().get_agent(conf['database_manager'])
        topology_manager = FactoryAgent().get_agent(conf['topology_manager'])
        try:
            topology = topology_manager.create(topology_args)
            checker = FactoryAgent().get_agent(conf['checker'])
            checker.check(topology=topology)
            db.persist(topology)
        except Exception, exc:
            logger.exception(exc.message)
            raise
        return topology


    @classmethod
    def update(cls, new_topology_args, old_topology):
        conf = sys_util().get_sys_conf()
        db = FactoryAgent().get_agent(conf['database_manager'])
        topology_manager = FactoryAgent().get_agent(conf['topology_manager'])
        checker = FactoryAgent().get_agent(conf['checker'])

        if old_topology.state in ['DEPLOYED','UPDATED']:
            old_topology.state = 'UPDATING'
        else:
            raise ActionInProgressException('Cannot update topology while another action is in progress. Topology state is \"%s\".' % old_topology.state)
        db.update(old_topology)

        try:
            new_topology = topology_manager.create(new_topology_args)
            checker.check(topology=new_topology)
            updated_topology = topology_manager.update(new_topology, old_topology)
            #checker.check(topology=updated_topology)
            db.update(updated_topology)
        except Exception, exc:
            logger.exception(exc.message)
            raise exc
        return updated_topology