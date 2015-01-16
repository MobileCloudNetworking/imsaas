from emm_exceptions import NotFoundException
from model.Entities import Topology
from services.DatabaseManager import DatabaseManager
from services.TopologyManager import TopologyManager
from services.Checker import check
__author__ = 'lto'


class TopologyOrchestrator:

    def __init__(self):
        pass

    @classmethod
    def delete(cls, topology):
        db = DatabaseManager()
        for service_instance in topology.service_instances:
                service_instance.networks = []
        db.update(topology)
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
            topology = TopologyManager().create(topology_args)
            #check(topology=topology)
            db = DatabaseManager()
            db.persist(topology)
        except Exception, msg:
            raise
        return topology
